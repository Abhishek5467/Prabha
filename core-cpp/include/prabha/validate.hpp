// prabha/validate.hpp — implements spec/validation-rules.md v0.1.0.
// Rule IDs MUST match core-py exactly; the conformance suite compares
// (rule, severity) multisets across engines.
#pragma once
#include <algorithm>
#include <map>
#include <set>
#include <string>
#include <vector>

#include <nlohmann/json.hpp>
#include "prabha/violation.hpp"
#include "prabha/registry.hpp"

namespace prabha {

inline const std::set<std::string> FANOUT_FORBIDDEN = {"optical", "current"};

using PortMap = std::map<std::string, json>;
using Pin = std::pair<std::string, std::string>;  // (instance, port)

inline PortMap ports_of(const json& defn, const std::string& side) {
    PortMap m;
    for (const auto& p : defn["ports"][side]) m[p["name"].get<std::string>()] = p;
    return m;
}

inline PortMap param_schema(const json& defn) {
    PortMap m;
    for (const auto& p : defn["params"]) m[p["name"].get<std::string>()] = p;
    return m;
}

inline std::string dom_of(const json& port) {
    return port.contains("domain") ? port["domain"].get<std::string>() : "time";
}

// ------------------------------------------------------------------
// Phases 1-3 on a netlist (top-level or a compound's subnetlist)
// ------------------------------------------------------------------
inline std::vector<Violation> validate_netlist(
        const json& netlist, const BlockRegistry& reg,
        const std::set<Pin>& boundary_inputs = {},
        const std::set<Pin>& boundary_outputs = {}) {
    std::vector<Violation> V;
    const auto& blocks = netlist["blocks"];
    const auto& conns = netlist["connections"];

    // R2 unique instance ids
    std::set<std::string> seen;
    for (const auto& b : blocks) {
        auto id = b["id"].get<std::string>();
        if (seen.count(id))
            V.push_back({"R2", "error", {{"instance", id}}, "duplicate instance id '" + id + "'"});
        seen.insert(id);
    }

    // R1 refs resolve
    std::map<std::string, json> inst;
    for (const auto& b : blocks) {
        auto id = b["id"].get<std::string>();
        auto ref = b["ref"].get<std::string>();
        if (!reg.contains(ref))
            V.push_back({"R1", "error", {{"instance", id}}, "unknown block definition '" + ref + "'"});
        else
            inst[id] = reg.get(ref);
    }

    // R4 params
    for (const auto& b : blocks) {
        auto id = b["id"].get<std::string>();
        if (!inst.count(id) || !b.contains("params")) continue;
        auto ps = param_schema(inst[id]);
        for (auto it = b["params"].begin(); it != b["params"].end(); ++it) {
            const std::string& k = it.key();
            const json& v = it.value();
            if (!ps.count(k)) {
                V.push_back({"R4", "error", {{"instance", id}, {"param", k}},
                             "unknown param '" + k + "'"});
                continue;
            }
            const json& sch = ps[k];
            const std::string t = sch["type"].get<std::string>();
            bool ok_type =
                (t == "number" && v.is_number() && !v.is_boolean()) ||
                (t == "string" && v.is_string()) ||
                (t == "boolean" && v.is_boolean()) ||
                (t == "enum" && v.is_string());
            if (!ok_type) {
                V.push_back({"R4", "error", {{"instance", id}, {"param", k}},
                             "param '" + k + "' type mismatch (expected " + t + ")"});
                continue;
            }
            if (t == "number") {
                double d = v.get<double>();
                bool bad = (sch.contains("min") && d < sch["min"].get<double>()) ||
                           (sch.contains("max") && d > sch["max"].get<double>());
                if (bad)
                    V.push_back({"R4", "error", {{"instance", id}, {"param", k}},
                                 "param '" + k + "' outside range"});
            }
            if (t == "enum") {
                bool found = false;
                for (const auto& o : sch["options"])
                    if (o.get<std::string>() == v.get<std::string>()) found = true;
                if (!found)
                    V.push_back({"R4", "error", {{"instance", id}, {"param", k}},
                                 "param '" + k + "' not in options"});
            }
        }
    }

    // R3 endpoints exist & direction; collect resolved
    struct Resolved { int ci; std::string fi; json fport; std::string ti; json tport; };
    std::vector<Resolved> resolved;
    int ci = 0;
    for (const auto& c : conns) {
        auto fi = c["from"][0].get<std::string>(), fp = c["from"][1].get<std::string>();
        auto ti = c["to"][0].get<std::string>(),   tp = c["to"][1].get<std::string>();
        bool bad = false;
        PortMap fouts, tins;
        if (!inst.count(fi)) {
            V.push_back({"R3", "error", {{"connection", std::to_string(ci)}},
                         "'from' instance '" + fi + "' unknown"}); bad = true;
        } else {
            fouts = ports_of(inst[fi], "outputs");
            if (!fouts.count(fp)) {
                V.push_back({"R3", "error", {{"instance", fi}, {"port", fp}},
                             "'" + fp + "' is not an output of '" + fi + "'"}); bad = true;
            }
        }
        if (!inst.count(ti)) {
            V.push_back({"R3", "error", {{"connection", std::to_string(ci)}},
                         "'to' instance '" + ti + "' unknown"}); bad = true;
        } else {
            tins = ports_of(inst[ti], "inputs");
            if (!tins.count(tp)) {
                V.push_back({"R3", "error", {{"instance", ti}, {"port", tp}},
                             "'" + tp + "' is not an input of '" + ti + "'"}); bad = true;
            }
        }
        if (!bad) resolved.push_back({ci, fi, fouts[fp], ti, tins[tp]});
        ++ci;
    }

    // R5 kind-match, R6 domain-match
    for (const auto& r : resolved) {
        if (r.fport["kind"].get<std::string>() != r.tport["kind"].get<std::string>())
            V.push_back({"R5", "error", {{"connection", std::to_string(r.ci)}}, "kind mismatch"});
        if (dom_of(r.fport) != dom_of(r.tport))
            V.push_back({"R6", "error", {{"connection", std::to_string(r.ci)}}, "domain mismatch"});
    }

    // R7 one driver per input
    std::map<Pin, int> targets;
    for (const auto& r : resolved)
        targets[{r.ti, r.tport["name"].get<std::string>()}]++;
    for (const auto& [pin, cnt] : targets)
        if (cnt > 1)
            V.push_back({"R7", "error", {{"instance", pin.first}, {"port", pin.second}},
                         "input has multiple drivers"});

    // R8 required inputs connected
    for (const auto& b : blocks) {
        auto id = b["id"].get<std::string>();
        if (!inst.count(id)) continue;
        for (const auto& p : inst[id]["ports"]["inputs"]) {
            bool optional = p.contains("optional") && p["optional"].get<bool>();
            if (optional) continue;
            Pin pin{id, p["name"].get<std::string>()};
            if (!targets.count(pin) && !boundary_inputs.count(pin))
                V.push_back({"R8", "error", {{"instance", pin.first}, {"port", pin.second}},
                             "required input unconnected"});
        }
    }

    // R9 unused outputs (warning) & R10 fan-out policy
    std::map<Pin, int> fanout;
    for (const auto& r : resolved)
        fanout[{r.fi, r.fport["name"].get<std::string>()}]++;
    for (const auto& b : blocks) {
        auto id = b["id"].get<std::string>();
        if (!inst.count(id)) continue;
        for (const auto& p : inst[id]["ports"]["outputs"]) {
            Pin pin{id, p["name"].get<std::string>()};
            int n = fanout.count(pin) ? fanout[pin] : 0;
            if (n == 0 && !boundary_outputs.count(pin))
                V.push_back({"R9", "warning", {{"instance", pin.first}, {"port", pin.second}},
                             "output unused"});
            if (n > 1 && FANOUT_FORBIDDEN.count(p["kind"].get<std::string>()))
                V.push_back({"R10", "error", {{"instance", pin.first}, {"port", pin.second}},
                             p["kind"].get<std::string>() +
                             " fan-out — insert an explicit splitter/divider block"});
        }
    }

    // R12 cycle detection (Kahn)
    std::vector<std::string> ids;
    for (const auto& b : blocks) ids.push_back(b["id"].get<std::string>());
    std::map<std::string, std::set<std::string>> deps;
    for (const auto& id : ids) deps[id] = {};
    for (const auto& r : resolved)
        if (r.fi != r.ti) deps[r.ti].insert(r.fi);
    std::vector<std::string> order, ready;
    std::set<std::string> queued;
    for (const auto& id : ids)
        if (deps[id].empty()) { ready.push_back(id); queued.insert(id); }
    while (!ready.empty()) {
        auto n0 = ready.back(); ready.pop_back();
        order.push_back(n0);
        for (const auto& m : ids) {
            if (deps[m].count(n0)) {
                deps[m].erase(n0);
                if (deps[m].empty() && !queued.count(m)) { ready.push_back(m); queued.insert(m); }
            }
        }
    }
    if (order.size() != ids.size())
        V.push_back({"R12", "error", {}, "feedback loops not yet supported (cycle detected)"});
    return V;
}

// ------------------------------------------------------------------
// Phase 4 — compound-definition rules (C1-C6) at load
// ------------------------------------------------------------------
inline std::vector<Violation> validate_compound_def(const json& defn, const BlockRegistry& reg) {
    std::vector<Violation> V;
    const std::string bid = defn["id"].get<std::string>();
    const json& sub = defn["subnetlist"];
    const json& bmap = defn["boundary_map"];
    auto exposed_in = ports_of(defn, "inputs");
    auto exposed_out = ports_of(defn, "outputs");

    // C1 bijection
    std::set<std::string> want, got;
    for (auto& [k, v] : exposed_in) want.insert(k);
    for (auto& [k, v] : exposed_out) want.insert(k);
    for (auto it = bmap.begin(); it != bmap.end(); ++it) got.insert(it.key());
    for (const auto& m : want)
        if (!got.count(m))
            V.push_back({"C1", "error", {{"block", bid}, {"port", m}},
                         "exposed port missing from boundary_map"});
    for (const auto& e : got)
        if (!want.count(e))
            V.push_back({"C1", "error", {{"block", bid}, {"port", e}},
                         "boundary_map key is not an exposed port"});

    std::map<std::string, json> inst;
    for (const auto& b : sub["blocks"]) inst[b["id"].get<std::string>()] = b;
    std::set<Pin> bin_set, bout_set;
    for (auto it = bmap.begin(); it != bmap.end(); ++it) {
        const std::string pname = it.key();
        const std::string ii = it.value()[0].get<std::string>();
        const std::string ip = it.value()[1].get<std::string>();
        if (!inst.count(ii) || !reg.contains(inst[ii]["ref"].get<std::string>())) {
            V.push_back({"C2", "error", {{"block", bid}, {"port", pname}},
                         "boundary target instance unknown"});
            continue;
        }
        const json& idef = reg.get(inst[ii]["ref"].get<std::string>());
        auto iin = ports_of(idef, "inputs"), iout = ports_of(idef, "outputs");
        json src, tgt;
        if (exposed_in.count(pname)) {
            if (!iin.count(ip)) {
                V.push_back({"C3", "error", {{"block", bid}, {"port", pname}},
                             "exposed input must map to an internal INPUT"});
                continue;
            }
            tgt = iin[ip]; src = exposed_in[pname]; bin_set.insert({ii, ip});
        } else if (exposed_out.count(pname)) {
            if (!iout.count(ip)) {
                V.push_back({"C3", "error", {{"block", bid}, {"port", pname}},
                             "exposed output must map to an internal OUTPUT"});
                continue;
            }
            tgt = iout[ip]; src = exposed_out[pname]; bout_set.insert({ii, ip});
        } else continue;  // C1 already reported
        if (src["kind"].get<std::string>() != tgt["kind"].get<std::string>() ||
            dom_of(src) != dom_of(tgt))
            V.push_back({"C3", "error", {{"block", bid}, {"port", pname}},
                         "boundary kind/domain mismatch"});
    }

    // C4 boundary-mapped internal input must not also have an internal driver
    for (const auto& c : sub["connections"]) {
        Pin pin{c["to"][0].get<std::string>(), c["to"][1].get<std::string>()};
        if (bin_set.count(pin))
            V.push_back({"C4", "error", {{"block", bid}, {"instance", pin.first}, {"port", pin.second}},
                         "internal input is boundary-mapped AND internally driven"});
    }

    // C6 subnetlist satisfies R1-R12 with boundary satisfied
    auto sv = validate_netlist(sub, reg, bin_set, bout_set);
    V.insert(V.end(), sv.begin(), sv.end());
    return V;
}

// C5: no compound block may (transitively) instantiate itself
inline std::vector<Violation> check_definition_cycles(const BlockRegistry& reg) {
    std::vector<Violation> V;
    enum { WHITE, GRAY, BLACK };
    std::map<std::string, int> color;
    for (auto& [id, d] : reg.defs) color[id] = WHITE;

    std::function<void(const std::string&)> dfs = [&](const std::string& bid) {
        color[bid] = GRAY;
        const json& d = reg.get(bid);
        if (d["block_type"].get<std::string>() == "compound") {
            for (const auto& b : d["subnetlist"]["blocks"]) {
                auto dep = b["ref"].get<std::string>();
                if (!reg.contains(dep)) continue;
                if (color[dep] == GRAY)
                    V.push_back({"C5", "error", {{"block", dep}}, "recursive compound definition"});
                else if (color[dep] == WHITE)
                    dfs(dep);
            }
        }
        color[bid] = BLACK;
    };
    for (auto& [id, d] : reg.defs)
        if (color[id] == WHITE) dfs(id);
    return V;
}

}  // namespace prabha
