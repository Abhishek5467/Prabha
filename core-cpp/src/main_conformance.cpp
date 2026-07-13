// main_conformance.cpp — C++ conformance runner.
// Implements the exact runner contract from spec/conformance/README.md:
// golden (exact + stats) and validation ((rule,severity) multisets, executed
// designs for runtime rules, expect_warnings). Exit 0 iff every fixture passes.
//
// Usage: prabha_conformance [PRABHA_ROOT]   (default: "..", i.e. run from core-cpp/)
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <filesystem>
#include <set>
#include <string>
#include <vector>

#include <nlohmann/json.hpp>
#include "prabha/signal.hpp"
#include "prabha/violation.hpp"
#include "prabha/registry.hpp"
#include "prabha/validate.hpp"
#include "prabha/engine.hpp"
#include "prabha/kernels.hpp"

namespace fs = std::filesystem;
using namespace prabha;

static BlockRegistry fresh_registry(const fs::path& root) {
    BlockRegistry reg;
    reg.load_dir(root / "spec" / "blocks");
    if (fs::exists(root / "blocks-lib")) reg.load_dir(root / "blocks-lib");
    return reg;
}

static double sample_of(std::map<std::string, std::map<std::string, Signal>>& res,
                        const json& spec) {
    const Signal& sig = res.at(spec["instance"].get<std::string>())
                           .at(spec["port"].get<std::string>());
    long long i = spec["sample"].get<long long>();
    if (sig.kind == Kind::Optical) {
        const auto& row = sig.optical[0];
        std::size_t idx = i < 0 ? row.size() + i : (std::size_t)i;
        return row[idx].real();
    }
    std::size_t idx = i < 0 ? sig.real.size() + i : (std::size_t)i;
    return sig.real[idx];
}

static std::vector<std::string> run_golden(const json& fx, const fs::path& root) {
    std::vector<std::string> fails;
    const json& ctx = fx["context"];
    if (!fx["expect"]["exact"].empty()) {
        System sys(fx["design"], fresh_registry(root),
                   {ctx["duration"].get<double>(), false,
                    ctx.contains("seed") ? ctx["seed"].get<int>() : 0});
        auto res = sys.run();
        for (const auto& e : fx["expect"]["exact"]) {
            double got = sample_of(res, e);
            double want = e["value"].get<double>();
            if (std::abs(got - want) > e["atol"].get<double>()) {
                char b[256];
                std::snprintf(b, sizeof b, "exact %s.%s: got %.12g want %.12g",
                              e["instance"].get<std::string>().c_str(),
                              e["port"].get<std::string>().c_str(), got, want);
                fails.push_back(b);
            }
        }
    }
    for (const auto& st : fx["expect"]["stats"]) {
        std::vector<double> vals;
        for (const auto& s : st["seeds"]) {
            System sys(fx["design"], fresh_registry(root),
                       {ctx["duration"].get<double>(), true, s.get<int>()});
            auto res = sys.run();
            vals.push_back(sample_of(res, st));
        }
        double mean = 0;
        for (double v : vals) mean += v;
        mean /= (double)vals.size();
        double var = 0;
        for (double v : vals) var += (v - mean) * (v - mean);
        double sd = std::sqrt(var / (double)vals.size());
        if (std::abs(mean - st["mean"].get<double>()) > st["mean_atol"].get<double>()) {
            char b[128];
            std::snprintf(b, sizeof b, "stats mean %.5f want %.5f +/- %.5f",
                          mean, st["mean"].get<double>(), st["mean_atol"].get<double>());
            fails.push_back(b);
        }
        if (sd > st["std_max"].get<double>()) {
            char b[128];
            std::snprintf(b, sizeof b, "stats std %.5f > max %.5f",
                          sd, st["std_max"].get<double>());
            fails.push_back(b);
        }
    }
    return fails;
}

using RS = std::set<std::pair<std::string, std::string>>;
static std::string rs_str(const RS& s) {
    std::string out = "[";
    for (auto& [r, sev] : s) out += r + "/" + sev + " ";
    return out + "]";
}

static std::vector<std::string> run_validation(const json& fx, const fs::path& root) {
    RS want, got, warns;
    for (const auto& v : fx["expect_violations"])
        want.insert({v["rule"].get<std::string>(), v["severity"].get<std::string>()});
    try {
        System sys(fx["design"], fresh_registry(root),
                   {fx["context"]["duration"].get<double>(), false, 0});
        for (const auto& w : sys.warnings) warns.insert({w.rule, w.severity});
        sys.run();  // runtime rules (R11) fire here
    } catch (const ValidationError& e) {
        for (const auto& v : e.violations) got.insert({v.rule, v.severity});
    }
    std::vector<std::string> fails;
    if (got != want)
        fails.push_back("violations got " + rs_str(got) + " want " + rs_str(want));
    if (fx.contains("expect_warnings")) {
        RS wwant;
        for (const auto& v : fx["expect_warnings"])
            wwant.insert({v["rule"].get<std::string>(), v["severity"].get<std::string>()});
        if (warns != wwant)
            fails.push_back("warnings got " + rs_str(warns) + " want " + rs_str(wwant));
    }
    return fails;
}

int main(int argc, char** argv) {
    const fs::path root = argc > 1 ? fs::path(argv[1]) : fs::path("..");
    int total = 0, failed = 0;
    struct Kind_ { const char* dir; std::vector<std::string> (*fn)(const json&, const fs::path&); };
    for (const Kind_& k : {Kind_{"golden", run_golden}, Kind_{"validation", run_validation}}) {
        std::vector<fs::path> files;
        for (auto& e : fs::directory_iterator(root / "spec" / "conformance" / k.dir))
            if (e.path().extension() == ".json") files.push_back(e.path());
        std::sort(files.begin(), files.end());
        for (const auto& p : files) {
            ++total;
            json fx = load_json(p);
            std::vector<std::string> fails;
            try {
                fails = k.fn(fx, root);
            } catch (const ValidationError&) {
                fails.push_back("unexpected ValidationError");
            } catch (const std::exception& ex) {
                fails.push_back(std::string("exception: ") + ex.what());
            }
            if (!fails.empty()) ++failed;
            std::printf("[%-10s] %-28s %s\n", k.dir,
                        fx["name"].get<std::string>().c_str(),
                        fails.empty() ? "PASS" : "FAIL");
            for (const auto& f : fails) std::printf("    - %s\n", f.c_str());
        }
    }
    std::printf("\n%d/%d fixtures pass\n", total - failed, total);
    return failed ? 1 : 0;
}
