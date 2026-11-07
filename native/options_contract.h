#pragma once
#include <cstdint>
namespace nitrogen::options {
struct Function { uint32_t address, size; uint64_t hash; uint32_t guard[4]; };
struct Binding { bool enabled; Function presentation, audio, title, title_caller; };
}
