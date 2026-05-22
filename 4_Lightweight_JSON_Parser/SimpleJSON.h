// SimpleJSON.h
// Lightweight JSON parser for simple key-value dictionaries.
// Extracted from GOTG Translation Mod.

#pragma once

#include <string>
#include <unordered_map>
#include <fstream>
#include <iostream>

class SimpleJSON {
public:
    static std::unordered_map<std::string, std::string> LoadDictionary(const std::string& filepath) {
        std::unordered_map<std::string, std::string> dict;
        std::ifstream f(filepath);
        
        if (!f.good()) {
            return dict;
        }

        std::string content((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());

        auto find_closing_quote = [&](size_t start) -> size_t {
            for (size_t p = start; p < content.size(); ++p) {
                if (content[p] == '\\') { ++p; continue; } // skip escaped char
                if (content[p] == '"') return p;
            }
            return std::string::npos;
        };

        size_t pos = 0;
        while (pos < content.size()) {
            size_t key_start = content.find('"', pos);
            if (key_start == std::string::npos) break;
            size_t key_end = find_closing_quote(key_start + 1);
            if (key_end == std::string::npos) break;

            size_t val_start = content.find('"', key_end + 1);
            if (val_start == std::string::npos) break;
            size_t val_end = find_closing_quote(val_start + 1);
            if (val_end == std::string::npos) break;

            std::string key = content.substr(key_start + 1, key_end - key_start - 1);
            std::string val = content.substr(val_start + 1, val_end - val_start - 1);

            // Handle basic escaped characters (e.g., \n)
            size_t escape_pos = 0;
            while ((escape_pos = val.find("\\n", escape_pos)) != std::string::npos) {
                val.replace(escape_pos, 2, "\n");
                escape_pos += 1;
            }

            if (!key.empty() && !val.empty()) {
                dict[key] = val;
            }

            pos = val_end + 1;
        }
        
        return dict;
    }
};
