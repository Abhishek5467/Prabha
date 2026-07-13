// tests/run_conformance.cpp — implements the runner contract from
// spec/conformance/README.md. Usage: run_conformance <repo root>.
// Exit 0 iff every fixture passes — the definition of a conforming engine.
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <numeric>

#include "prabha/engine.hpp"

namespace fs = std::filesystem;
using prabha::json;

static json read_json(const fs::path& p) {
    std::ifstream f(p);
    json j;
    f >> j;
    return j;
}

static prabha::BlockRegistry fresh_registry(const fs::path& root) {
    prabha::BlockRegistry reg;
    reg.load_dir(root / "spec" / "blocks");
    for (auto& e : fs::directory_iterator(root / "blocks-lib"))
        if (e.path().extension() == ".json") reg.load_file(e.path());
    return reg;
}

static double sample(const std::map<std::string, std::map<std::string, prabha::Signal>>& res,
                     const json& spec) {
    const auto& sig = res.at(spec.at("instance").get<std::string>())
                          .at(spec.at("port").get<std::string>());
    long long i = spec.at("sample").get<long long>();
    if (sig.kind == prabha::Kind::Optical) {
        if (i < 0) i += static_cast<long long>(sig.cdata.size());
        return std::abs(sig.cdata[static_cast<std::size_t>(i)]);
    }
    if (i < 0) i += static_cast<long long>(sig.rdata.size());
    return sig.rdata[static_cast<std::size_t>(i)];
}

static std::vector<std::string> run_golden(const json& fx, const fs::path& root) {
    std::vector<std::string> fails;
    const json& ctx = fx.at("context");
    if (!fx.at("expect").at("exact").empty()) {
        auto reg = fresh_registry(root);
        prabha::System sys(fx.at("design"), reg,
                           {ctx.at("duration").get<double>(), false,
                            ctx.value("seed", 0LL)});
        auto res = sys.run();
        for (const auto& e : fx.at("expect").at("exact")) {
            const double got = sample(res, e);
            const double want = e.at("value").get<double>();
            if (std::abs(got - want) > e.at("atol").get<double>())
                fails.push_back("exact " + e.at("instance").get<std::string>() + "." +
                                e.at("port").get<std::string>() + ": got " +
                                std::to_string(got) + " want " + std::to_string(want));
        }
    }
    for (const auto& st : fx.at("expect").at("stats")) {
        std::vector<double> vals;
        for (const auto& s : st.at("seeds")) {
            auto reg = fresh_registry(root);
            prabha::System sys(fx.at("design"), reg,
                               {ctx.at("duration").get<double>(), true, s.get<long long>()});
            auto res = sys.run();
            vals.push_back(sample(res, st));
        }
        const double mean = std::accumulate(vals.begin(), vals.end(), 0.0) / vals.size();
        double var = 0;
        for (double v : vals) var += (v - mean) * (v - mean);
        const double sd = std::sqrt(var / vals.size());
        if (std::abs(mean - st.at("mean").get<double>()) > st.at("mean_atol").get<double>())
            fails.push_back("stats mean " + std::to_string(mean) + " want " +
                            std::to_string(st.at("mean").get<double>()));
        if (sd > st.at("std_max").get<double>())
            fails.push_back("stats std " + std::to_string(sd) + " > max " +
                            std::to_string(st.at("std_max").get<double>()));
    }
    return fails;
}

static std::vector<std::string> run_validation(const json& fx, const fs::path& root) {
    using RS = std::pair<std::string, std::string>;
    std::set<RS> want, got, warns;
    for (const auto& v : fx.at("expect_violations"))
        want.insert({v.at("rule").get<std::string>(), v.at("severity").get<std::string>()});
    try {
        auto reg = fresh_registry(root);
        prabha::System sys(fx.at("design"), reg,
                           {fx.at("context").at("duration").get<double>(), false, 0});
        for (const auto& w : sys.warnings) warns.insert({w.rule, w.severity});
        sys.run();  // runtime rules (R11)
    } catch (const prabha::ValidationError& e) {
        for (const auto& v : e.violations) got.insert({v.rule, v.severity});
    }
    std::vector<std::string> fails;
    auto show = [](const std::set<RS>& s) {
        std::string o = "{";
        for (const auto& [r, sv] : s) o += r + ",";
        return o + "}";
    };
    if (got != want) fails.push_back("violations got " + show(got) + " want " + show(want));
    if (fx.contains("expect_warnings")) {
        std::set<RS> wwant;
        for (const auto& v : fx.at("expect_warnings"))
            wwant.insert({v.at("rule").get<std::string>(), v.at("severity").get<std::string>()});
        if (warns != wwant) fails.push_back("warnings got " + show(warns) + " want " + show(wwant));
    }
    return fails;
}

int main(int argc, char** argv) {
    const fs::path root = argc > 1 ? argv[1] : fs::current_path();
    int total = 0, failed = 0;
    struct KindSpec { const char* dir; std::vector<std::string> (*fn)(const json&, const fs::path&); };
    for (const auto& [dir, fn] : std::vector<KindSpec>{{"golden", run_golden},
                                                       {"validation", run_validation}}) {
        std::vector<fs::path> files;
        for (auto& e : fs::directory_iterator(root / "spec" / "conformance" / dir))
            if (e.path().extension() == ".json") files.push_back(e.path());
        std::sort(files.begin(), files.end());
        for (const auto& p : files) {
            ++total;
            const json fx = read_json(p);
            std::vector<std::string> fails;
            try {
                fails = fn(fx, root);
            } catch (const std::exception& ex) {
                fails = {std::string("exception: ") + ex.what()};
            }
            if (!fails.empty()) ++failed;
            std::cout << "[" << dir << (dir == std::string("golden") ? "    " : "") << "] "
                      << fx.at("name").get<std::string>() << "  "
                      << (fails.empty() ? "PASS" : "FAIL") << "\n";
            for (const auto& f : fails) std::cout << "    - " << f << "\n";
        }
    }
    std::cout << "\n" << (total - failed) << "/" << total << " fixtures pass\n";
    return failed ? 1 : 0;
}
