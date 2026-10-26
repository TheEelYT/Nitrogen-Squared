#pragma once
#include <cstdint>
namespace nitrogen::media {
struct MovieExtent { const char *name; uint32_t lba, sectors; };
struct Binding {
    bool enabled;
    uint32_t entry, index_address, body_size, guard[4];
    uint64_t body_hash;
    MovieExtent clips[4];
};
}
