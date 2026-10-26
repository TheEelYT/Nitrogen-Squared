/* Original native media interfaces. Inputs remain on the player's disc. */
#pragma once
#include <cstdint>
#include <memory>
#include <mutex>
#include <string>
#include <vector>
namespace nitrogen::media {
struct Packet {
    uint32_t number = 0, width = 0, height = 0, end_sector = 0;
    std::vector<uint8_t> bytes;
    double pts() const { return (end_sector + 1) / 150.0; }
};
struct Clip {
    std::vector<Packet> video;
    std::vector<int16_t> audio;
    uint32_t sample_rate = 37800;
    double duration = 0;
};
struct Frame {
    uint32_t width = 0, height = 0;
    double pts = 0;
    std::vector<uint32_t> argb;
};
class XaDecoder {
    int32_t history[2][2]{};
public:
    std::vector<int16_t> decode(const uint8_t *sector, size_t bytes);
};
Clip read_clip(const std::string &bin, uint32_t lba, uint32_t sectors, unsigned channel = 1);
class VideoDecoder {
    std::unique_lock<std::mutex> owner;
public:
    VideoDecoder();
    ~VideoDecoder();
    VideoDecoder(const VideoDecoder &) = delete;
    VideoDecoder &operator=(const VideoDecoder &) = delete;
    Frame decode(const Packet &packet);
};
std::vector<uint16_t> decode_vlc(const Packet &packet);
}
