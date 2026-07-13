// prabha/signal.hpp — C++ mirror of core-py/prabha/signal.py.
// Same contract as spec/schema/signal.schema.json: kind/domain/fs/units metadata
// plus sample data (RAM only; never serialized into .prabha files).
//
// Conventions (identical to core-py):
//   optical  -> complex<double> envelope in sqrt(W); one row per channel
//   voltage  -> double, Volts
//   current  -> double, Amps
//   digital  -> double, code
#pragma once
#include <complex>
#include <stdexcept>
#include <string>
#include <vector>

namespace prabha {

enum class Kind { Optical, Voltage, Current, Digital };
enum class Domain { Time, Frequency };

inline const char* to_string(Kind k) {
    switch (k) {
        case Kind::Optical: return "optical";
        case Kind::Voltage: return "voltage";
        case Kind::Current: return "current";
        case Kind::Digital: return "digital";
    }
    return "?";
}

inline Kind kind_from(const std::string& s) {
    if (s == "optical") return Kind::Optical;
    if (s == "voltage") return Kind::Voltage;
    if (s == "current") return Kind::Current;
    if (s == "digital") return Kind::Digital;
    throw std::invalid_argument("unknown kind: " + s);
}

// Lumerical-faithful channel identity: frequency canonical; polarization is a
// value of mode_label (TE0/TM0); wavelength derived, never stored.
struct Channel {
    double frequency;                 // Hz, canonical
    std::string mode_label = "TE0";
    int orthogonal_id = 0;

    double wavelength() const { return 299792458.0 / frequency; }
};

inline Channel default_channel() { return Channel{299792458.0 / 1550e-9}; }

struct Signal {
    Kind kind;
    Domain domain = Domain::Time;
    double fs = 0.0;                  // sample rate (time) / grid spacing (frequency)
    std::string units;

    // exactly one of these is populated, by kind:
    std::vector<std::vector<std::complex<double>>> optical;  // [channel][sample]
    std::vector<double> real;                                // voltage/current/digital

    std::vector<Channel> channels;    // optical only

    std::size_t n() const {
        return kind == Kind::Optical ? (optical.empty() ? 0 : optical[0].size())
                                     : real.size();
    }

    // Forward-compat guard, mirrors Signal.single_channel() in core-py:
    // single-channel blocks assert here so a WDM signal fails loudly, not silently.
    const std::vector<std::complex<double>>& single_channel() const {
        if (kind != Kind::Optical)
            throw std::logic_error("single_channel() on non-optical signal");
        if (channels.size() != 1)
            throw std::runtime_error("block supports 1 optical channel, got " +
                                     std::to_string(channels.size()));
        return optical[0];
    }
};

// factory helpers (units defaulted exactly as core-py DEFAULT_UNITS)
inline Signal make_electrical(Kind k, double fs, std::vector<double> data) {
    Signal s;
    s.kind = k;
    s.fs = fs;
    s.real = std::move(data);
    s.units = (k == Kind::Voltage) ? "V" : (k == Kind::Current) ? "A" : "code";
    return s;
}

inline Signal make_optical(double fs, std::vector<std::complex<double>> env,
                           std::vector<Channel> ch = {default_channel()}) {
    Signal s;
    s.kind = Kind::Optical;
    s.fs = fs;
    s.units = "sqrt(W)";
    s.channels = std::move(ch);
    s.optical.push_back(std::move(env));
    if (s.optical.size() != s.channels.size())
        throw std::runtime_error("optical rows != channels");
    return s;
}

}  // namespace prabha
