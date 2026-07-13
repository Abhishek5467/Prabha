#include "prabha/registry.hpp"
#include <fstream>
#include <stdexcept>

namespace prabha {

static json read_json(const std::filesystem::path& p) {
    std::ifstream f(p);
    if (!f) throw std::runtime_error("cannot open " + p.string());
    json j;
    f >> j;
    return j;
}

void BlockRegistry::load_dir(const std::filesystem::path& dir) {
    std::vector<std::filesystem::path> files;
    for (auto& e : std::filesystem::directory_iterator(dir)) {
        auto ext = e.path().extension().string();
        if (ext == ".json" || ext == ".prabha") files.push_back(e.path());
    }
    std::sort(files.begin(), files.end());
    for (auto& p : files) load_file(p);
}

void BlockRegistry::load_file(const std::filesystem::path& file) {
    add(read_json(file), file.string());
}

void BlockRegistry::add(json doc, const std::string& source) {
    const std::string id = doc.at("id").get<std::string>();
    if (defs_.count(id))
        throw std::runtime_error("duplicate block definition id '" + id + "' (from " + source + ")");
    defs_.emplace(id, std::move(doc));
}

json load_design(const std::filesystem::path& file) { return read_json(file); }

}  // namespace prabha
