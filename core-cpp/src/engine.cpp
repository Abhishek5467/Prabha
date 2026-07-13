// src/flatten.cpp — normative flattening (namespaced "parent/child" ids).
#include "prabha/engine.hpp"

namespace prabha {

json flatten(const json& netlist, const BlockRegistry& reg) {
    json blocks = netlist.at("blocks");
    json conns = netlist.at("connections");

    while (true) {
        int comp_idx = -1;
        for (int i = 0; i < static_cast<int>(blocks.size()); ++i) {
            const std::string ref = blocks[i].at("ref").get<std::string>();
            if (reg.contains(ref) &&
                reg.get(ref).at("block_type").get<std::string>() == "compound") {
                comp_idx = i;
                break;
            }
        }
        if (comp_idx < 0) break;

        json comp = blocks[comp_idx];
        blocks.erase(comp_idx);
        const std::string ns = comp.at("id").get<std::string>();
        const json& defn = reg.get(comp.at("ref").get<std::string>());
        const json& sub = defn.at("subnetlist");
        const json& bmap = defn.at("boundary_map");

        for (const auto& ib : sub.at("blocks")) {
            json nb = ib;
            nb["id"] = ns + "/" + ib.at("id").get<std::string>();
            blocks.push_back(nb);
        }
        for (const auto& ic : sub.at("connections")) {
            json nc;
            nc["from"] = {ns + "/" + ic.at("from")[0].get<std::string>(), ic.at("from")[1]};
            nc["to"] = {ns + "/" + ic.at("to")[0].get<std::string>(), ic.at("to")[1]};
            conns.push_back(nc);
        }
        for (auto& c : conns) {
            if (c.at("from")[0].get<std::string>() == ns) {
                const json& t = bmap.at(c.at("from")[1].get<std::string>());
                c["from"] = {ns + "/" + t[0].get<std::string>(), t[1]};
            }
            if (c.at("to")[0].get<std::string>() == ns) {
                const json& t = bmap.at(c.at("to")[1].get<std::string>());
                c["to"] = {ns + "/" + t[0].get<std::string>(), t[1]};
            }
        }
    }
    return json{{"blocks", blocks}, {"connections", conns}};
}

// ---------------------------------------------------------------------------
// engine: kernel registry + System (load-time C rules, flatten, R rules, run)
// ---------------------------------------------------------------------------
std::map<std::string, KernelFactory>& kernel_registry() {
    static std::map<std::string, KernelFactory> r;
    return r;
}

System::System(const json& design, const BlockRegistry& reg, RunContext ctx)
    : reg_(reg), ctx_(ctx) {
    std::vector<Violation> vio = check_definition_cycles(reg);
    for (const auto& [bid, defn] : reg.defs())
        if (defn.at("block_type").get<std::string>() == "compound") {
            auto v = validate_compound_def(defn, reg);
            vio.insert(vio.end(), v.begin(), v.end());
        }

    flat = flatten(design, reg);
    auto v = validate_netlist(flat, reg);
    vio.insert(vio.end(), v.begin(), v.end());

    std::vector<Violation> errors;
    for (auto& x : vio)
        (x.severity == "warning" ? warnings : errors).push_back(x);
    if (!errors.empty()) throw ValidationError(std::move(errors));

    for (const auto& b : flat.at("blocks")) {
        const std::string id = b.at("id").get<std::string>();
        const json& defn = reg.get(b.at("ref").get<std::string>());
        const std::string impl = defn.at("implementation").get<std::string>();
        auto it = kernel_registry().find(impl);
        if (it == kernel_registry().end())
            throw std::runtime_error("no kernel registered for implementation '" + impl + "'");
        json params;
        for (const auto& p : defn.at("params"))
            params[p.at("name").get<std::string>()] = p.at("default");
        if (b.contains("params"))
            for (auto pit = b.at("params").begin(); pit != b.at("params").end(); ++pit)
                params[pit.key()] = pit.value();
        kernels_[id] = it->second(std::move(params), ctx_, id);
    }
}

std::vector<std::string> System::topo() const {
    std::vector<std::string> ids;
    for (const auto& b : flat.at("blocks")) ids.push_back(b.at("id").get<std::string>());
    std::map<std::string, std::set<std::string>> deps;
    for (const auto& i : ids) deps[i] = {};
    for (const auto& c : flat.at("connections"))
        deps[c.at("to")[0].get<std::string>()].insert(c.at("from")[0].get<std::string>());
    std::vector<std::string> order, ready;
    std::set<std::string> seen;
    for (const auto& i : ids)
        if (deps[i].empty()) ready.push_back(i);
    std::sort(ready.begin(), ready.end());
    for (const auto& r : ready) seen.insert(r);
    while (!ready.empty()) {
        auto n = ready.front();
        ready.erase(ready.begin());
        order.push_back(n);
        for (const auto& m : ids)
            if (deps[m].count(n)) {
                deps[m].erase(n);
                if (deps[m].empty() && !seen.count(m)) { ready.push_back(m); seen.insert(m); }
            }
    }
    return order;
}

std::map<std::string, std::map<std::string, Signal>> System::run() {
    std::map<std::pair<std::string, std::string>, Signal> buf;
    std::map<std::string, std::map<std::string, Signal>> results;
    for (const auto& nid : topo()) {
        std::map<std::string, const Signal*> inputs;
        for (const auto& c : flat.at("connections"))
            if (c.at("to")[0].get<std::string>() == nid)
                inputs[c.at("to")[1].get<std::string>()] =
                    &buf.at({c.at("from")[0].get<std::string>(),
                             c.at("from")[1].get<std::string>()});
        // R11 runtime: all time-domain inputs share fs
        std::set<double> fss;
        for (const auto& [k, s] : inputs)
            if (s && s->domain == "time") fss.insert(s->fs);
        if (fss.size() > 1)
            throw ValidationError({{"R11", "error", {{"instance", nid}}, "fs mismatch"}});
        auto out = kernels_.at(nid)->process(inputs);
        for (auto& [pname, sig] : out) buf[{nid, pname}] = sig;
        results[nid] = std::move(out);
    }
    return results;
}

}  // namespace prabha
