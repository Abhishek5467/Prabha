// src/validate.cpp — implements spec/validation-rules.md v0.1.0.
// Rule IDs and severities MUST match core-py exactly (conformance-tested).
#include "prabha/engine.hpp"
#include <algorithm>

namespace prabha {

static const std::set<std::string> FANOUT_FORBIDDEN = {"optical", "current"};

using PortMap = std::map<std::string, json>;
using PP = std::pair<std::string, std::string>;

static PortMap ports_of(const json& defn, const char* side) {
    PortMap m;
    for (const auto& p : defn.at("ports").at(side)) m[p.at("name").get<std::string>()] = p;
    return m;
}
static std::map<std::string, json> param_schema(const json& defn) {
    std::map<std::string, json> m;
    for (const auto& p : defn.at("params")) m[p.at("name").get<std::string>()] = p;
    return m;
}
static std::string dom(const json& port) {
    return port.contains("domain") ? port.at("domain").get<std::string>() : "time";
}

std::vector<Violation> validate_netlist(const json& netlist, const BlockRegistry& reg,
                                        const std::set<PP>& boundary_inputs,
                                        const std::set<PP>& boundary_outputs) {
    std::vector<Violation> V;
    const auto& blocks = netlist.at("blocks");
    const auto& conns = netlist.at("connections");

    // R2 unique instance ids
    std::set<std::string> seen;
    for (const auto& b : blocks) {
        const auto id = b.at("id").get<std::string>();
        if (seen.count(id))
            V.push_back({"R2", "error", {{"instance", id}}, "duplicate instance id '" + id + "'"});
        seen.insert(id);
    }

    // R1 refs resolve
    std::map<std::string, const json*> inst;
    for (const auto& b : blocks) {
        const auto id = b.at("id").get<std::string>();
        const auto ref = b.at("ref").get<std::string>();
        if (!reg.contains(ref))
            V.push_back({"R1", "error", {{"instance", id}}, "unknown block definition '" + ref + "'"});
        else
            inst[id] = &reg.get(ref);
    }

    // R4 params
    for (const auto& b : blocks) {
        const auto id = b.at("id").get<std::string>();
        if (!inst.count(id) || !b.contains("params")) continue;
        auto ps = param_schema(*inst[id]);
        for (auto it = b.at("params").begin(); it != b.at("params").end(); ++it) {
            const std::string k = it.key();
            const json& v = it.value();
            if (!ps.count(k)) {
                V.push_back({"R4", "error", {{"instance", id}, {"param", k}},
                             "unknown param '" + k + "'"});
                continue;
            }
            const json& sch = ps[k];
            const std::string t = sch.at("type").get<std::string>();
            bool ok = (t == "number" && v.is_number() && !v.is_boolean()) ||
                      (t == "string" && v.is_string()) ||
                      (t == "boolean" && v.is_boolean()) ||
                      (t == "enum" && v.is_string());
            if (!ok) {
                V.push_back({"R4", "error", {{"instance", id}, {"param", k}},
                             "param '" + k + "' type mismatch (expected " + t + ")"});
                continue;
            }
            if (t == "number") {
                double x = v.get<double>();
                if ((sch.contains("min") && x < sch["min"].get<double>()) ||
                    (sch.contains("max") && x > sch["max"].get<double>()))
                    V.push_back({"R4", "error", {{"instance", id}, {"param", k}},
                                 "param '" + k + "' outside [min,max]"});
            }
            if (t == "enum") {
                bool found = false;
                for (const auto& o : sch.at("options"))
                    if (o.get<std::string>() == v.get<std::string>()) found = true;
                if (!found)
                    V.push_back({"R4", "error", {{"instance", id}, {"param", k}},
                                 "param '" + k + "' not in options"});
            }
        }
    }

    // R3 endpoints exist & direction; collect resolved connections
    struct RC { int ci; std::string fi; json fport; std::string ti; json tport; };
    std::vector<RC> resolved;
    for (int ci = 0; ci < static_cast<int>(conns.size()); ++ci) {
        const auto& c = conns[ci];
        const std::string fi = c.at("from")[0], fp = c.at("from")[1];
        const std::string ti = c.at("to")[0], tp = c.at("to")[1];
        bool bad = false;
        PortMap fo, tin;
        if (!inst.count(fi)) {
            V.push_back({"R3", "error", {{"connection", std::to_string(ci)}},
                         "'from' instance '" + fi + "' unknown"});
            bad = true;
        } else {
            fo = ports_of(*inst[fi], "outputs");
            if (!fo.count(fp)) {
                V.push_back({"R3", "error",
                             {{"connection", std::to_string(ci)}, {"instance", fi}, {"port", fp}},
                             "'" + fp + "' is not an output of '" + fi + "'"});
                bad = true;
            }
        }
        if (!inst.count(ti)) {
            V.push_back({"R3", "error", {{"connection", std::to_string(ci)}},
                         "'to' instance '" + ti + "' unknown"});
            bad = true;
        } else {
            tin = ports_of(*inst[ti], "inputs");
            if (!tin.count(tp)) {
                V.push_back({"R3", "error",
                             {{"connection", std::to_string(ci)}, {"instance", ti}, {"port", tp}},
                             "'" + tp + "' is not an input of '" + ti + "'"});
                bad = true;
            }
        }
        if (!bad) resolved.push_back({ci, fi, fo[fp], ti, tin[tp]});
    }

    // R5 kind-match, R6 domain-match
    for (const auto& r : resolved) {
        if (r.fport.at("kind") != r.tport.at("kind"))
            V.push_back({"R5", "error", {{"connection", std::to_string(r.ci)}},
                         "kind mismatch on connection"});
        if (dom(r.fport) != dom(r.tport))
            V.push_back({"R6", "error", {{"connection", std::to_string(r.ci)}},
                         "domain mismatch on connection"});
    }

    // R7 one driver per input
    std::map<PP, int> targets;
    for (const auto& r : resolved) targets[{r.ti, r.tport.at("name").get<std::string>()}]++;
    for (const auto& [k, cnt] : targets)
        if (cnt > 1)
            V.push_back({"R7", "error", {{"instance", k.first}, {"port", k.second}},
                         "input has multiple drivers"});

    // R8 required inputs connected
    for (const auto& b : blocks) {
        const auto id = b.at("id").get<std::string>();
        if (!inst.count(id)) continue;
        for (const auto& p : inst[id]->at("ports").at("inputs")) {
            if (p.value("optional", false)) continue;
            PP key{id, p.at("name").get<std::string>()};
            if (!targets.count(key) && !boundary_inputs.count(key))
                V.push_back({"R8", "error", {{"instance", id}, {"port", key.second}},
                             "required input unconnected"});
        }
    }

    // R9 unused outputs (warning), R10 fan-out policy
    std::map<PP, int> fanout;
    for (const auto& r : resolved) fanout[{r.fi, r.fport.at("name").get<std::string>()}]++;
    for (const auto& b : blocks) {
        const auto id = b.at("id").get<std::string>();
        if (!inst.count(id)) continue;
        for (const auto& p : inst[id]->at("ports").at("outputs")) {
            PP key{id, p.at("name").get<std::string>()};
            int n = fanout.count(key) ? fanout[key] : 0;
            if (n == 0 && !boundary_outputs.count(key))
                V.push_back({"R9", "warning", {{"instance", id}, {"port", key.second}},
                             "output unused"});
            if (n > 1 && FANOUT_FORBIDDEN.count(p.at("kind").get<std::string>()))
                V.push_back({"R10", "error", {{"instance", id}, {"port", key.second}},
                             "optical/current fan-out — insert an explicit splitter/divider"});
        }
    }

    // R12 cycle detection (Kahn)
    std::vector<std::string> ids;
    for (const auto& b : blocks) ids.push_back(b.at("id").get<std::string>());
    std::map<std::string, std::set<std::string>> deps;
    for (const auto& i : ids) deps[i] = {};
    for (const auto& r : resolved)
        if (r.fi != r.ti) deps[r.ti].insert(r.fi);
    std::vector<std::string> order, ready;
    std::set<std::string> seen2;
    for (const auto& i : ids)
        if (deps[i].empty()) { ready.push_back(i); seen2.insert(i); }
    while (!ready.empty()) {
        auto n0 = ready.back();
        ready.pop_back();
        order.push_back(n0);
        for (const auto& m : ids)
            if (deps[m].count(n0)) {
                deps[m].erase(n0);
                if (deps[m].empty() && !seen2.count(m)) { ready.push_back(m); seen2.insert(m); }
            }
    }
    if (order.size() != ids.size())
        V.push_back({"R12", "error", {},
                     "feedback loops not yet supported (cycle detected)"});
    return V;
}

// ---------------------------------------------------------------- C1-C6 -----
std::vector<Violation> validate_compound_def(const json& defn, const BlockRegistry& reg) {
    std::vector<Violation> V;
    const std::string bid = defn.at("id").get<std::string>();
    const json& sub = defn.at("subnetlist");
    const json& bmap = defn.at("boundary_map");
    auto exposed_in = ports_of(defn, "inputs");
    auto exposed_out = ports_of(defn, "outputs");

    // C1 bijection
    std::set<std::string> want, got;
    for (const auto& [k, v] : exposed_in) want.insert(k);
    for (const auto& [k, v] : exposed_out) want.insert(k);
    for (auto it = bmap.begin(); it != bmap.end(); ++it) got.insert(it.key());
    for (const auto& m : want)
        if (!got.count(m))
            V.push_back({"C1", "error", {{"block", bid}, {"port", m}},
                         "exposed port missing from boundary_map"});
    for (const auto& e : got)
        if (!want.count(e))
            V.push_back({"C1", "error", {{"block", bid}, {"port", e}},
                         "boundary_map key is not an exposed port"});

    std::map<std::string, const json*> inst;
    for (const auto& b : sub.at("blocks")) inst[b.at("id").get<std::string>()] = &b;
    std::set<PP> bin_set, bout_set;
    for (auto it = bmap.begin(); it != bmap.end(); ++it) {
        const std::string pname = it.key();
        const std::string ii = it.value()[0], ip = it.value()[1];
        if (!inst.count(ii) || !reg.contains(inst[ii]->at("ref").get<std::string>())) {
            V.push_back({"C2", "error", {{"block", bid}, {"port", pname}},
                         "boundary target instance unknown"});
            continue;
        }
        const json& idef = reg.get(inst[ii]->at("ref").get<std::string>());
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
        } else {
            continue;  // C1 already reported
        }
        if (src.at("kind") != tgt.at("kind") || dom(src) != dom(tgt))
            V.push_back({"C3", "error", {{"block", bid}, {"port", pname}},
                         "boundary kind/domain mismatch"});
    }

    // C4 boundary-mapped internal input must not also be internally driven
    for (const auto& c : sub.at("connections")) {
        PP key{c.at("to")[0].get<std::string>(), c.at("to")[1].get<std::string>()};
        if (bin_set.count(key))
            V.push_back({"C4", "error",
                         {{"block", bid}, {"instance", key.first}, {"port", key.second}},
                         "internal input is boundary-mapped AND internally driven"});
    }

    // C6 subnetlist satisfies R1-R12 with boundary ports satisfied
    auto sub_v = validate_netlist(sub, reg, bin_set, bout_set);
    V.insert(V.end(), sub_v.begin(), sub_v.end());
    return V;
}

std::vector<Violation> check_definition_cycles(const BlockRegistry& reg) {
    std::vector<Violation> V;
    enum { WHITE, GRAY, BLACK };
    std::map<std::string, int> color;
    for (const auto& [id, d] : reg.defs()) color[id] = WHITE;

    std::function<void(const std::string&)> dfs = [&](const std::string& bid) {
        color[bid] = GRAY;
        const json& d = reg.get(bid);
        if (d.at("block_type").get<std::string>() == "compound") {
            for (const auto& b : d.at("subnetlist").at("blocks")) {
                const std::string dep = b.at("ref").get<std::string>();
                if (!reg.contains(dep)) continue;
                if (color[dep] == GRAY)
                    V.push_back({"C5", "error", {{"block", dep}},
                                 "recursive compound definition"});
                else if (color[dep] == WHITE)
                    dfs(dep);
            }
        }
        color[bid] = BLACK;
    };
    for (const auto& [id, d] : reg.defs())
        if (color[id] == WHITE) dfs(id);
    return V;
}

}  // namespace prabha
