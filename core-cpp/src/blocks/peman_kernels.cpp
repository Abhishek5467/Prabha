// src/blocks/peman_kernels.cpp — physics port of core-py peman_primitives.py.
// Noiseless math must match Python to ~1e-9 (same operation order). Noise uses
// std::mt19937_64 (stream differs from NumPy PCG64 — conformance compares
// noise STATISTICS only, per spec/conformance/README.md).
#include <cfenv>
#include <cmath>
#include <random>
#include <sstream>

#include "prabha/engine.hpp"

namespace prabha {

static constexpr double QE = 1.602176634e-19;
static constexpr double KB = 1.380649e-23;
static constexpr double C0 = 299792458.0;

static std::vector<double> vec(const json& v) {
    std::vector<double> out;
    if (v.is_array()) { for (const auto& x : v) out.push_back(x.get<double>()); return out; }
    std::stringstream ss(v.get<std::string>());
    std::string tok;
    while (std::getline(ss, tok, ',')) if (!tok.empty()) out.push_back(std::stod(tok));
    return out;
}

// ----------------------------------------------------------------- laser ----
struct CWLaser : Kernel {
    using Kernel::Kernel;
    std::map<std::string, Signal> process(const std::map<std::string, const Signal*>&) override {
        const double fs = p.at("fs").get<double>();
        const auto n = static_cast<std::size_t>(std::llround(fs * ctx.duration));
        const double P0 = p.at("P0").get<double>() * 1e-3;
        std::mt19937_64 rng(seed);
        std::normal_distribution<double> N01(0.0, 1.0);
        const double sphi = std::sqrt(2.0 * M_PI * p.at("linewidth").get<double>() / fs);
        const double rin = std::pow(10.0, p.at("RIN").get<double>() / 10.0);
        const double sdP = std::sqrt(rin * fs / 2.0) * P0;
        std::vector<std::complex<double>> E(n);
        double phi = 0.0;
        for (std::size_t k = 0; k < n; ++k) {
            double P = P0;
            if (ctx.noise) { phi += sphi * N01(rng); P += sdP * N01(rng); }
            if (P < 0) P = 0;
            E[k] = std::sqrt(P) * std::complex<double>(std::cos(phi), std::sin(phi));
        }
        Signal s;
        s.kind = Kind::Optical; s.fs = fs; s.units = "sqrt(W)";
        s.channels = {Channel{C0 / (p.at("wavelength").get<double>() * 1e-9)}};
        s.cdata = std::move(E);
        return {{"out", std::move(s)}};
    }
};
PRABHA_REGISTER_KERNEL("CWLaser", CWLaser)

// ---------------------------------------------------------------- drives ----
static Signal piecewise(const std::vector<double>& vals, double rateGHz, int sps,
                        double duration) {
    const double fs = rateGHz * 1e9 * sps;
    const auto n = static_cast<std::size_t>(std::llround(fs * duration));
    std::vector<double> w(n);
    for (std::size_t k = 0; k < n; ++k) {
        std::size_t idx = k / static_cast<std::size_t>(sps);
        if (idx >= vals.size()) idx = vals.size() - 1;
        w[k] = vals[idx];
    }
    Signal s; s.kind = Kind::Voltage; s.fs = fs; s.units = "V"; s.rdata = std::move(w);
    return s;
}

struct DriveSource : Kernel {
    using Kernel::Kernel;
    std::map<std::string, Signal> process(const std::map<std::string, const Signal*>&) override {
        return {{"out", piecewise(vec(p.at("values")), p.at("rate").get<double>(),
                                  static_cast<int>(p.at("sps").get<double>()), ctx.duration)}};
    }
};
PRABHA_REGISTER_KERNEL("DriveSource", DriveSource)

struct WeightSource : Kernel {
    using Kernel::Kernel;
    std::map<std::string, Signal> process(const std::map<std::string, const Signal*>&) override {
        auto w = vec(p.at("values"));
        std::vector<double> tu(w.size()), tl(w.size());
        for (std::size_t i = 0; i < w.size(); ++i) { tu[i] = (1 + w[i]) / 2; tl[i] = (1 - w[i]) / 2; }
        const double r = p.at("rate").get<double>();
        const int sps = static_cast<int>(p.at("sps").get<double>());
        return {{"upper", piecewise(tu, r, sps, ctx.duration)},
                {"lower", piecewise(tl, r, sps, ctx.duration)}};
    }
};
PRABHA_REGISTER_KERNEL("WeightSource", WeightSource)

// -------------------------------------------------------------- photonic ----
struct IntensityModulator : Kernel {
    using Kernel::Kernel;
    std::map<std::string, Signal> process(const std::map<std::string, const Signal*>& in) override {
        const Signal& opt = *in.at("in");
        const auto& E = opt.single_channel();
        const auto& d = in.at("drive")->rdata;
        const std::size_t n = std::min(E.size(), d.size());
        std::vector<std::complex<double>> out(n);
        for (std::size_t k = 0; k < n; ++k) {
            double t = d[k]; t = t < 0 ? 0 : (t > 1 ? 1 : t);
            out[k] = E[k] * std::sqrt(t);
        }
        return {{"out", opt.like_c(std::move(out))}};
    }
};
PRABHA_REGISTER_KERNEL("IntensityModulator", IntensityModulator)

struct Splitter : Kernel {
    using Kernel::Kernel;
    std::map<std::string, Signal> process(const std::map<std::string, const Signal*>& in) override {
        const Signal& opt = *in.at("in");
        const auto& E = opt.single_channel();
        const double r = p.at("ratio").get<double>();
        const double a = std::sqrt(r), b = std::sqrt(1 - r);
        std::vector<std::complex<double>> o1(E.size()), o2(E.size());
        for (std::size_t k = 0; k < E.size(); ++k) { o1[k] = E[k] * a; o2[k] = E[k] * b; }
        return {{"out1", opt.like_c(std::move(o1))}, {"out2", opt.like_c(std::move(o2))}};
    }
};
PRABHA_REGISTER_KERNEL("Splitter", Splitter)

// ------------------------------------------------------------- detection ----
struct Photodetector : Kernel {
    using Kernel::Kernel;
    std::map<std::string, Signal> process(const std::map<std::string, const Signal*>& in) override {
        const Signal& opt = *in.at("in");
        const auto& E = opt.single_channel();
        const double resp = p.at("resp").get<double>(), dark = p.at("dark").get<double>();
        std::vector<double> I(E.size());
        for (std::size_t k = 0; k < E.size(); ++k) I[k] = resp * std::norm(E[k]) + dark;
        if (ctx.noise) {
            std::mt19937_64 rng(seed);
            std::normal_distribution<double> N01(0.0, 1.0);
            const double bw = opt.fs / 2.0;
            const double th = 4 * KB * p.at("Trx").get<double>() * bw / p.at("load").get<double>();
            for (auto& x : I) {
                const double sh = 2 * QE * (x > 0 ? x : 0) * bw;
                x += std::sqrt(sh + th) * N01(rng);
            }
        }
        Signal s; s.kind = Kind::Current; s.fs = opt.fs; s.units = "A"; s.rdata = std::move(I);
        return {{"I", std::move(s)}};
    }
};
PRABHA_REGISTER_KERNEL("Photodetector", Photodetector)

struct BalancedPair : Kernel {
    using Kernel::Kernel;
    std::map<std::string, Signal> process(const std::map<std::string, const Signal*>& in) override {
        const auto& a = in.at("i1")->rdata;
        const auto& b = in.at("i2")->rdata;
        const std::size_t n = std::min(a.size(), b.size());
        std::vector<double> o(n);
        for (std::size_t k = 0; k < n; ++k) o[k] = a[k] - b[k];
        return {{"I", in.at("i1")->like(std::move(o))}};
    }
};
PRABHA_REGISTER_KERNEL("BalancedPair", BalancedPair)

// ------------------------------------------------------------ electronic ----
struct CapacitorIntegrator : Kernel {
    using Kernel::Kernel;
    std::map<std::string, Signal> process(const std::map<std::string, const Signal*>& in) override {
        const Signal& s = *in.at("I");
        const double C = p.at("C").get<double>() * 1e-12;
        std::vector<double> v(s.rdata.size());
        double acc = 0.0;
        for (std::size_t k = 0; k < s.rdata.size(); ++k) {
            acc += s.rdata[k];
            v[k] = acc / s.fs / C;
        }
        Signal out; out.kind = Kind::Voltage; out.fs = s.fs; out.units = "V"; out.rdata = std::move(v);
        return {{"Vc", std::move(out)}};
    }
};
PRABHA_REGISTER_KERNEL("CapacitorIntegrator", CapacitorIntegrator)

struct BiasGain : Kernel {
    using Kernel::Kernel;
    std::map<std::string, Signal> process(const std::map<std::string, const Signal*>& in) override {
        const Signal& s = *in.at("in");
        const double g = p.at("gain").get<double>(), th = p.at("theta").get<double>();
        std::vector<double> o(s.rdata.size());
        for (std::size_t k = 0; k < o.size(); ++k) o[k] = g * s.rdata[k] + th;
        return {{"out", s.like(std::move(o))}};
    }
};
PRABHA_REGISTER_KERNEL("BiasGain", BiasGain)

struct ADC : Kernel {
    using Kernel::Kernel;
    std::map<std::string, Signal> process(const std::map<std::string, const Signal*>& in) override {
        const Signal& s = *in.at("in");
        const double vmin = p.at("vmin").get<double>(), vmax = p.at("vmax").get<double>();
        const double L = std::pow(2.0, p.at("bits").get<double>());
        std::vector<double> o(s.rdata.size());
        std::fesetround(FE_TONEAREST);  // nearbyint == round-half-to-even == np.round
        for (std::size_t k = 0; k < o.size(); ++k) {
            double x = (s.rdata[k] - vmin) / (vmax - vmin);
            x = x < 0 ? 0 : (x > 1 ? 1 : x);
            const double code = std::nearbyint(x * (L - 1));
            o[k] = vmin + code / (L - 1) * (vmax - vmin);
        }
        Signal out; out.kind = Kind::Digital; out.fs = s.fs; out.units = "code"; out.rdata = std::move(o);
        return {{"code", std::move(out)}};
    }
};
PRABHA_REGISTER_KERNEL("ADC", ADC)

struct Activation : Kernel {
    using Kernel::Kernel;
    std::map<std::string, Signal> process(const std::map<std::string, const Signal*>& in) override {
        const Signal& s = *in.at("in");
        const std::string kind = p.at("kind").get<std::string>();
        const double sc = p.at("scale").get<double>();
        std::vector<double> z(s.rdata.size());
        for (std::size_t k = 0; k < z.size(); ++k) {
            const double v = sc * s.rdata[k];
            z[k] = kind == "sigmoid" ? 1.0 / (1.0 + std::exp(-v))
                 : kind == "tanh"    ? std::tanh(v)
                                     : (v > 0 ? v : 0.0);
        }
        return {{"z", s.like(std::move(z))}};
    }
};
PRABHA_REGISTER_KERNEL("Activation", Activation)

}  // namespace prabha
