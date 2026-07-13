// prabha/registry.hpp — block-definition registry, mirror of core-py block.py.
//
// HONEST GAP (documented): core-py runs full JSON-Schema validation (Phase 0)
// via jsonschema. C++ has no bundled schema validator; structural validation
// here is minimal (required keys present). The conformance fixtures are all
// schema-valid by construction, so 14/14 is achievable; full Phase 0 in C++
// (e.g. via valijson) is future work, tracked in docs/decisions.
#pragma once
#include <filesystem>
#include <fstream>
#include <map>
#include <stdexcept>
#include <string>

#include <nlohmann/json.hpp>

namespace prabha {
using json = nlohmann::json;

class BlockRegistry {
public:
    std::map<std::string, json> defs;

    void add(const json& doc, const std::string& source = "<inline>") {
        for (const char* k : {"id", "title", "category", "block_type", "ports", "params"})
            if (!doc.contains(k))
                throw std::runtime_error("block definition " + source + " missing key: " + k);
        const std::string id = doc["id"].get<std::string>();
        if (defs.count(id))
            throw std::runtime_error("duplicate block definition id '" + id + "' (" + source + ")");
        defs[id] = doc;
    }

    void load_file(const std::filesystem::path& p) {
        std::ifstream f(p);
        if (!f) throw std::runtime_error("cannot open " + p.string());
        add(json::parse(f), p.string());
    }

    void load_dir(const std::filesystem::path& d) {
        std::vector<std::filesystem::path> files;
        for (auto& e : std::filesystem::directory_iterator(d)) {
            auto ext = e.path().extension().string();
            if (ext == ".json" || ext == ".prabha") files.push_back(e.path());
        }
        std::sort(files.begin(), files.end());
        for (auto& p : files) load_file(p);
    }

    bool contains(const std::string& id) const { return defs.count(id) != 0; }
    const json& get(const std::string& id) const { return defs.at(id); }
};

inline json load_json(const std::filesystem::path& p) {
    std::ifstream f(p);
    if (!f) throw std::runtime_error("cannot open " + p.string());
    return json::parse(f);
}

}  // namespace prabha
