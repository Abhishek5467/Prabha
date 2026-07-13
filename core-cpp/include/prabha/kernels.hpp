// prabha/kernels.hpp — the 11 PEMAN primitive kernels, ported from
// core-py/prabha/blocks/peman_primitives.py. Noiseless math must match core-py
// to ~1e-9 (same operations, same order); noise is statistical-only per the
// conformance policy (RNG streams don't port; statistics do).
//
// Rounding note: numpy's np.round is round-half-to-EVEN. std::nearbyint under
// the default FE_TONEAREST mode is also half-to-even — that is why the ADC uses
// nearbyint and NOT std::round (which is half-away-from-zero).
#pragma once
#include <cfenv>
#include <cmath>
#include <complex>
#include <random>
#include <sstream>

#include "prabha/engine.hpp"

namespace prabha {

constexpr double Q_E = 1.602176634e-19;
constexpr double K_B = 1.380649e-23;
constexpr double PI = 3.14159265358979323846;

inline std::vector<double> parse_vec(const json& v) {
    std::vector<double> out;
    if (v.is_array()) { for (const auto& x : v) out.push_back(x.get<double>()); return out; }
    std::stringstream ss(v.get<std::string>());
    std::string tok;
    while (std::getline(ss, tok, ',')) if (!tok.empty()) out.push_back(std::stod(tok));
    return out;
}

// piecewise-constant waveform, identical indexing to core-py DriveSource
inline std::vector<double> pwl(const std::vector<double>& vals, double fs,
                               int sps, double duration) {
    const std::size_t n = (std::size_t)std::llround(fs * duration);
    std::vector<double> out(n);
    for (std::size_t k = 0; k < n; ++k) {
        std::size_t idx = std::min<std::size_t>(k / (std::size_t)sps, vals.size() - 1);
        out[k] = vals[idx];
    }
    return out;
}

// ---------------- Sources ----------------
class CWLaser : public Kernel {
public:
    std::map<std::string, Signal> process(std::map<std::string, const Signal*>&) override {
        const double fs = num("fs");
        const std::size_t n = (std::size_t)std::llround(fs * ctx.duration);
        const double P0 = num("P0") * 1e-3;
        std::mt19937_64 rng(seed);
        std::normal_distribution<double> N01(0.0, 1.0);
        const double dphi_sd = std::sqrt(2.0 * PI * num("linewidth") / fs);
        const double rin = std::pow(10.0, num("RIN") / 10.0);
        const double dP_sd = std::sqrt(rin * fs / 2.0) * P0;
        std::vector<std::complex<double>> E(n);
        double phi = 0.0;
        for (std::size_t k = 0; k < n; ++k) {
            double P = P0;
            if (ctx.noise) {
                phi += dphi_sd * N01(rng);
                P = std::max(0.0, P0 + dP_sd * N01(rng));
            }
            E[k] = std::sqrt(P) * std::complex<double>(std::cos(phi), std::sin(phi));
        }
        Channel ch{299792458.0 / (num("wavelength") * 1e-9)};
        return {{"out", make_optical(fs, std::move(E), {ch})}};
    }
};
PRABHA_KERNEL("CWLaser", CWLaser)

class DriveSource : public Kernel {
public:
    std::map<std::string, Signal> process(std::map<std::string, const Signal*>&) override {
        auto vals = parse_vec(p.at("values"));
        const int sps = (int)num("sps");
        const double fs = num("rate") * 1e9 * sps;
        return {{"out", make_electrical(Kind::Voltage, fs, pwl(vals, fs, sps, ctx.duration))}};
    }
};
PRABHA_KERNEL("DriveSource", DriveSource)

class WeightSource : public Kernel {
public:
    std::map<std::string, Signal> process(std::map<std::string, const Signal*>&) override {
        auto w = parse_vec(p.at("values"));
        std::vector<double> tu(w.size()), tl(w.size());
        for (std::size_t i = 0; i < w.size(); ++i) { tu[i] = (1 + w[i]) / 2; tl[i] = (1 - w[i]) / 2; }
        const int sps = (int)num("sps");
        const double fs = num("rate") * 1e9 * sps;
        return {{"upper", make_electrical(Kind::Voltage, fs, pwl(tu, fs, sps, ctx.duration))},
                {"lower", make_electrical(Kind::Voltage, fs, pwl(tl, fs, sps, ctx.duration))}};
    }
};
PRABHA_KERNEL("WeightSource", WeightSource)

// ---------------- Photonic ----------------
class IntensityModulator : public Kernel {
public:
    std::map<std::string, Signal> process(std::map<std::string, const Signal*>& in) override {
        const auto& E = in.at("in")->single_channel();
        const auto& d = in.at("drive")->real;
        const std::size_t n = std::min(E.size(), d.size());
        std::vector<std::complex<double>> out(n);
        for (std::size_t k = 0; k < n; ++k) {
            double t = std::min(1.0, std::max(0.0, d[k]));
            out[k] = E[k] * std::sqrt(t);
        }
        return {{"out", make_optical(in.at("in")->fs, std::move(out), in.at("in")->channels)}};
    }
};
PRABHA_KERNEL("IntensityModulator", IntensityModulator)

class Splitter : public Kernel {
public:
    std::map<std::string, Signal> process(std::map<std::string, const Signal*>& in) override {
        const auto& E = in.at("in")->single_channel();
        const double r = num("ratio");
        const double a = std::sqrt(r), b = std::sqrt(1 - r);
        std::vector<std::complex<double>> o1(E.size()), o2(E.size());
        for (std::size_t k = 0; k < E.size(); ++k) { o1[k] = E[k] * a; o2[k] = E[k] * b; }
        return {{"out1", make_optical(in.at("in")->fs, std::move(o1), in.at("in")->channels)},
                {"out2", make_optical(in.at("in")->fs, std::move(o2), in.at("in")->channels)}};
    }
};
PRABHA_KERNEL("Splitter", Splitter)

// ---------------- Detection ----------------
class Photodetector : public Kernel {
public:
    std::map<std::string, Signal> process(std::map<std::string, const Signal*>& in) override {
        const Signal& sin_ = *in.at("in");
        const auto& E = sin_.single_channel();
        const double resp = num("resp"), dark = num("dark");
        std::vector<double> I(E.size());
        for (std::size_t k = 0; k < E.size(); ++k) I[k] = resp * std::norm(E[k]) + dark;
        if (ctx.noise) {
            std::mt19937_64 rng(seed);
            std::normal_distribution<double> N01(0.0, 1.0);
            const double bw = sin_.fs / 2.0;
            const double therm = 4.0 * K_B * num("Trx") * bw / num("load");
            for (auto& i : I) {
                double var = 2.0 * Q_E * std::max(i, 0.0) * bw + therm;
                i += std::sqrt(var) * N01(rng);
            }
        }
        return {{"I", make_electrical(Kind::Current, sin_.fs, std::move(I))}};
    }
};
PRABHA_KERNEL("Photodetector", Photodetector)

class BalancedPair : public Kernel {
public:
    std::map<std::string, Signal> process(std::map<std::string, const Signal*>& in) override {
        const auto& a = in.at("i1")->real;
        const auto& b = in.at("i2")->real;
        const std::size_t n = std::min(a.size(), b.size());
        std::vector<double> out(n);
        for (std::size_t k = 0; k < n; ++k) out[k] = a[k] - b[k];
        return {{"I", make_electrical(Kind::Current, in.at("i1")->fs, std::move(out))}};
    }
};
PRABHA_KERNEL("BalancedPair", BalancedPair)

// ---------------- Electronic ----------------
class CapacitorIntegrator : public Kernel {
public:
    std::map<std::string, Signal> process(std::map<std::string, const Signal*>& in) override {
        const Signal& s = *in.at("I");
        const double C = num("C") * 1e-12;
        std::vector<double> v(s.real.size());
        double acc = 0.0;
        for (std::size_t k = 0; k < s.real.size(); ++k) {
            acc += s.real[k];                 // cumsum, then scale — matches numpy order
            v[k] = acc / s.fs / C;
        }
        return {{"Vc", make_electrical(Kind::Voltage, s.fs, std::move(v))}};
    }
};
PRABHA_KERNEL("CapacitorIntegrator", CapacitorIntegrator)

class BiasGain : public Kernel {
public:
    std::map<std::string, Signal> process(std::map<std::string, const Signal*>& in) override {
        const Signal& s = *in.at("in");
        const double g = num("gain"), th = num("theta");
        std::vector<double> v(s.real.size());
        for (std::size_t k = 0; k < v.size(); ++k) v[k] = g * s.real[k] + th;
        return {{"out", make_electrical(Kind::Voltage, s.fs, std::move(v))}};
    }
};
PRABHA_KERNEL("BiasGain", BiasGain)

class ADC : public Kernel {
public:
    std::map<std::string, Signal> process(std::map<std::string, const Signal*>& in) override {
        const Signal& s = *in.at("in");
        const double L = std::pow(2.0, num("bits"));
        const double vmin = num("vmin"), vmax = num("vmax");
        std::vector<double> v(s.real.size());
        for (std::size_t k = 0; k < v.size(); ++k) {
            double x = std::min(1.0, std::max(0.0, (s.real[k] - vmin) / (vmax - vmin)));
            double code = std::nearbyint(x * (L - 1));   // half-to-even, matches np.round
            v[k] = vmin + code / (L - 1) * (vmax - vmin);
        }
        return {{"code", make_electrical(Kind::Digital, s.fs, std::move(v))}};
    }
};
PRABHA_KERNEL("ADC", ADC)

// ---------------- Output ----------------
class Activation : public Kernel {
public:
    std::map<std::string, Signal> process(std::map<std::string, const Signal*>& in) override {
        const Signal& s = *in.at("in");
        const double sc = num("scale");
        const std::string kind = str("kind");
        std::vector<double> z(s.real.size());
        for (std::size_t k = 0; k < z.size(); ++k) {
            double u = sc * s.real[k];
            z[k] = kind == "sigmoid" ? 1.0 / (1.0 + std::exp(-u))
                 : kind == "tanh"    ? std::tanh(u)
                                     : std::max(0.0, u);
        }
        return {{"z", make_electrical(Kind::Digital, s.fs, std::move(z))}};
    }
};
PRABHA_KERNEL("Activation", Activation)

}  // namespace prabha
