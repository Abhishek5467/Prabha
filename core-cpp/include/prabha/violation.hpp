// prabha/violation.hpp — the machine-readable violation record from
// spec/validation-rules.md. Rule IDs MUST match core-py exactly; the
// conformance suite compares (rule, severity) multisets across engines.
#pragma once
#include <map>
#include <string>
#include <vector>

namespace prabha {

struct Violation {
    std::string rule;                       // "R1".."R12", "C1".."C6"
    std::string severity;                   // "error" | "warning"
    std::map<std::string, std::string> where;
    std::string message;
};

struct ValidationError {                    // thrown when errors block a run
    std::vector<Violation> violations;
};

}  // namespace prabha
