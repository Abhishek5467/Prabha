// prabha/engine.hpp — flattener + execution engine, mirror of compound.py/engine.py.
// Pipeline: (minimal Phase 0) -> C1-C6 + C5 at load -> flatten -> R1-R12 -> run.
// R11 (fs-match) is enforced at runtime; per-instance noise seed is
// CRC32(instance_id) + run_seed + block 'seed' param — identical to core-py.
#pragma once
#include <cstdint>
#include <functional>
#include <map>
#include <memory>
#include <random>
#include <string>
#include <vector>

#include <nlohmann/json.hpp>
#include "prabha/signal.hpp"
#include "prabha/violation.hpp"
#include "prabha/registry.hpp"
#include "prabha/validate.hpp"

namespace prabha {

// CRC-32 (IEEE), matches Python zlib.crc32 — verified cross-language.
inline std::uint32_t crc32(const std::string& s) {
    std::uint32_t c = 0xFFFFFFFFu;
    for (unsigned char ch : s) {
        c ^= ch;
        for (int k = 0; k < 8; ++k)
            c = (c >> 1) ^ (0xEDB88320u & (0u - (c & 1u)));
    }
    return ~c;
}

// ------------------------------------------------------------------
// Flattening (normative procedure from validation-rules.md)
// ------------------------------------------------------------------
inline json flatten(const json& netlist, const BlockRegistry& reg) {
    json blocks = netlist["blocks"];
    json conns = netlist["connections"];

    while (true) {
        int idx = -1;
        for (int i = 0; i < (int)blocks.size(); ++i) {
            auto ref = blocks[i]["ref"].get<std::string>();
            if (reg.contains(ref) && reg.get(ref)["block_type"] == "compound") { idx = i; break; }
        }
        if (idx < 0) break;

        json comp = blocks[idx];
        blocks.erase(idx);
        const json& defn = reg.get(comp["ref"].get<std::string>());
        const std::string ns = comp["id"].get<std::string>();
        const json& sub = defn["subnetlist"];
        const json& bmap = defn["boundary_map"];

        for (const auto& ib : sub["blocks"]) {
            json nb = ib;
            nb["id"] = ns + "/" + ib["id"].get<std::string>();
            blocks.push_back(nb);
        }
        for (const auto& ic : sub["connections"]) {
            json nc;
            nc["from"] = {ns + "/" + ic["from"][0].get<std::string>(), ic["from"][1]};
            nc["to"] = {ns + "/" + ic["to"][0].get<std::string>(), ic["to"][1]};
            conns.push_back(nc);
        }
        for (auto& c : conns) {
            if (c["from"][0].get<std::string>() == ns) {
                const json& m = bmap[c["from"][1].get<std::string>()];
                c["from"] = {ns + "/" + m[0].get<std::string>(), m[1]};
            }
            if (c["to"][0].get<std::string>() == ns) {
                const json& m = bmap[c["to"][1].get<std::string>()];
                c["to"] = {ns + "/" + m[0].get<std::string>(), m[1]};
            }
        }
    }
    json out;
    out["blocks"] = blocks;
    out["connections"] = conns;
    return out;
}

// ------------------------------------------------------------------
// Kernels
// ------------------------------------------------------------------
struct RunContext {
    double duration;
    bool noise = true;
    int seed = 0;
};

class Kernel {
public:
    json p;
    RunContext ctx;
    std::string instance_id;
    std::uint32_t seed = 0;

    virtual ~Kernel() = default;
    virtual std::map<std::string, Signal> process(std::map<std::string, const Signal*>& in) = 0;

    void init(const json& params, const RunContext& c, const std::string& id) {
        p = params; ctx = c; instance_id = id;
        long long extra = p.contains("seed") ? (long long)p["seed"].get<double>() : 0;
        seed = (std::uint32_t)((crc32(id) + (long long)c.seed + extra) & 0xFFFFFFFFll);
    }
    double num(const char* k) const { return p.at(k).get<double>(); }
    std::string str(const char* k) const { return p.at(k).get<std::string>(); }
};

using KernelFactory = std::function<std::unique_ptr<Kernel>()>;
inline std::map<std::string, KernelFactory>& kernel_registry() {
    static std::map<std::string, KernelFactory> r;
    return r;
}
template <class K>
struct KernelRegistrar {
    explicit KernelRegistrar(const char* name) {
        kernel_registry()[name] = [] { return std::unique_ptr<Kernel>(new K()); };
    }
};
#define PRABHA_KERNEL(NAME, CLASS) \
    static ::prabha::KernelRegistrar<CLASS> _reg_##CLASS(NAME);

// ------------------------------------------------------------------
// System — construct = validate per spec order; run = topo schedule
// ------------------------------------------------------------------
class System {
public:
    const BlockRegistry& reg;
    RunContext ctx;
    json flat;
    std::vector<Violation> warnings;
    std::map<std::string, std::unique_ptr<Kernel>> kernels;

    System(const json& design, const BlockRegistry& r, RunContext c) : reg(r), ctx(c) {
        std::vector<Violation> vio = check_definition_cycles(reg);
        for (const auto& [bid, defn] : reg.defs)
            if (defn["block_type"] == "compound") {
                auto cv = validate_compound_def(defn, reg);
                vio.insert(vio.end(), cv.begin(), cv.end());
            }
        flat = flatten(design, reg);
        auto nv = validate_netlist(flat, reg);
        vio.insert(vio.end(), nv.begin(), nv.end());

        std::vector<Violation> errors;
        for (auto& v : vio)
            (v.severity == "warning" ? warnings : errors).push_back(v);
        if (!errors.empty()) throw ValidationError{errors};

        for (const auto& b : flat["blocks"]) {
            const std::string id = b["id"].get<std::string>();
            const json& defn = reg.get(b["ref"].get<std::string>());
            const std::string impl = defn["implementation"].get<std::string>();
            auto it = kernel_registry().find(impl);
            if (it == kernel_registry().end())
                throw std::runtime_error("no kernel registered for implementation '" + impl + "'");
            json params = json::object();
            for (const auto& pr : defn["params"])
                params[pr["name"].get<std::string>()] = pr["default"];
            if (b.contains("params"))
                for (auto pit = b["params"].begin(); pit != b["params"].end(); ++pit)
                    params[pit.key()] = pit.value();
            auto k = it->second();
            k->init(params, ctx, id);
            kernels[id] = std::move(k);
        }
    }

    std::vector<std::string> topo() const {
        std::vector<std::string> ids;
        for (const auto& b : flat["blocks"]) ids.push_back(b["id"].get<std::string>());
        std::map<std::string, std::set<std::string>> deps;
        for (const auto& id : ids) deps[id] = {};
        for (const auto& c : flat["connections"])
            deps[c["to"][0].get<std::string>()].insert(c["from"][0].get<std::string>());
        std::vector<std::string> order, ready;
        std::set<std::string> queued;
        for (const auto& id : ids)
            if (deps[id].empty()) { ready.push_back(id); queued.insert(id); }
        std::sort(ready.begin(), ready.end());
        while (!ready.empty()) {
            auto n = ready.front(); ready.erase(ready.begin());
            order.push_back(n);
            for (const auto& m : ids)
                if (deps[m].count(n)) {
                    deps[m].erase(n);
                    if (deps[m].empty() && !queued.count(m)) { ready.push_back(m); queued.insert(m); }
                }
        }
        return order;
    }

    std::map<std::string, std::map<std::string, Signal>> run() {
        // zero-copy: results is the single store; buf holds pointers into it
        // (M3 optimization item 1 from the architecture roadmap)
        std::map<std::pair<std::string, std::string>, const Signal*> buf;
        std::map<std::string, std::map<std::string, Signal>> results;
        for (const auto& nid : topo()) {
            std::map<std::string, const Signal*> inputs;
            for (const auto& c : flat["connections"])
                if (c["to"][0].get<std::string>() == nid)
                    inputs[c["to"][1].get<std::string>()] =
                        buf.at({c["from"][0].get<std::string>(), c["from"][1].get<std::string>()});
            // R11 runtime: all time-domain inputs share fs
            std::set<double> fss;
            for (auto& [k, s] : inputs)
                if (s && s->domain == Domain::Time) fss.insert(s->fs);
            if (fss.size() > 1)
                throw ValidationError{{{"R11", "error", {{"instance", nid}}, "fs mismatch"}}};
            results[nid] = kernels[nid]->process(inputs);
            for (auto& [pname, sig] : results[nid]) buf[{nid, pname}] = &sig;
        }
        return results;
    }
};

}  // namespace prabha
