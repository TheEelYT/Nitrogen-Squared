/* Original bounded STR bit reader, packet assembly and XA decoder. */
#include "media.h"
#include "mdec_host.h"
#include "mpeg_tables.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstring>
#include <fstream>
#include <stdexcept>
namespace nitrogen::media {
namespace {
uint16_t u16(const uint8_t *p) { return (uint16_t)(p[0] | p[1] << 8); }
uint32_t u32(const uint8_t *p) { return u16(p) | (uint32_t)u16(p + 2) << 16; }
void require(bool good, const char *message) { if (!good) throw std::runtime_error(message); }
std::mutex decoder_mutex;
constexpr uint8_t scan[64] = {
    0,1,8,16,9,2,3,10,17,24,32,25,18,11,4,5,
    12,19,26,33,40,48,41,34,27,20,13,6,7,14,21,28,
    35,42,49,56,57,50,43,36,29,22,15,23,30,37,44,51,
    58,59,52,45,38,31,39,46,53,60,61,54,47,55,62,63
};
class Bits {
    const std::vector<uint8_t> &bytes;
    size_t position = 64;
    uint32_t word(size_t at) const { return at + 1 < bytes.size() ? u16(&bytes[at]) : 0; }
public:
    explicit Bits(const std::vector<uint8_t> &b) : bytes(b) {}
    uint16_t peek() const {
        const size_t at = (position / 16) * 2;
        return (uint16_t)(((word(at) << 16 | word(at + 2)) >> (16 - position % 16)) & 65535);
    }
    unsigned get(unsigned count) {
        require(count <= 16 && position + count <= bytes.size() * 8, "Truncated STR bitstream");
        const unsigned value = count ? peek() >> (16 - count) : 0;
        position += count; return value;
    }
};
struct Lookup {
    std::array<int16_t, 65536> symbol;
    std::array<uint8_t, 65536> length;
    Lookup() { symbol.fill(-1); length.fill(0); }
    void add(unsigned code, unsigned bits, unsigned index) {
        require(bits > 0 && bits <= 16 && code < (1u << bits), "Invalid VLC codebook");
        const unsigned begin = code << (16 - bits), end = begin + (1u << (16 - bits));
        for (unsigned key = begin; key < end; ++key) {
            require(symbol[key] < 0, "Overlapping VLC codebook");
            symbol[key] = (int16_t)index; length[key] = (uint8_t)bits;
        }
    }
    unsigned take(Bits &bits) const {
        unsigned key = bits.peek(); require(symbol[key] >= 0, "Invalid STR VLC symbol");
        bits.get(length[key]); return (unsigned)symbol[key];
    }
};
struct Codebooks {
    Lookup ac, luma, chroma;
    Codebooks() {
        for (unsigned i = 0; i < 113; ++i) ac.add(tables::vlc_table[i][0], tables::vlc_table[i][1], i);
        for (unsigned i = 0; i < 12; ++i) {
            luma.add(tables::vlc_dc_lum_code[i], tables::vlc_dc_lum_bits[i], i);
            chroma.add(tables::vlc_dc_chroma_code[i], tables::vlc_dc_chroma_bits[i], i);
        }
    }
};
int signed10(unsigned value) { return value & 512 ? (int)value - 1024 : (int)value; }
int floor64(int value) { return value >= 0 ? value / 64 : -((-value + 63) / 64); }
}
std::vector<uint16_t> decode_vlc(const Packet &packet)
{
    require(packet.width > 0 && packet.width <= 640 && packet.height > 0 && packet.height <= 480, "Unsupported STR dimensions");
    require(packet.bytes.size() >= 8 && packet.bytes.size() <= 1024 * 1024 && !(packet.bytes.size() & 1), "Invalid STR packet length");
    const unsigned q = u16(packet.bytes.data() + 4), version = u16(packet.bytes.data() + 6);
    require(q < 64 && (version == 2 || version == 3), "Unsupported STR bitstream version");
    static const Codebooks codes;
    Bits bits(packet.bytes);
    int dc[3] = {128,128,128};
    const unsigned macroblocks = ((packet.width + 15) / 16) * ((packet.height + 15) / 16);
    std::vector<uint16_t> out; out.reserve(macroblocks * 24);
    for (unsigned mb = 0; mb < macroblocks; ++mb) {
        for (unsigned block = 0; block < 6; ++block) {
            const unsigned component = block == 0 ? 2 : block == 1 ? 1 : 0;
            int coefficient;
            if (version == 2) coefficient = signed10(bits.get(10));
            else {
                const unsigned size = (component ? codes.chroma : codes.luma).take(bits);
                const unsigned raw = bits.get(size);
                const int delta = size && raw < (1u << (size - 1)) ? (int)raw - (int)((1u << size) - 1) : (int)raw;
                dc[component] += delta; coefficient = (dc[component] - 128) * 4;
                require(coefficient >= -512 && coefficient <= 511, "Invalid STR DC prediction");
            }
            out.push_back((uint16_t)(q << 10 | ((unsigned)coefficient & 1023)));
            unsigned position = 0;
            for (;;) {
                const unsigned symbol = codes.ac.take(bits);
                if (symbol == 112) { out.push_back(0xfe00); break; }
                unsigned run; int level;
                if (symbol == 111) { run = bits.get(6); level = signed10(bits.get(10)); }
                else { run = tables::run[symbol]; level = tables::level[symbol]; if (bits.get(1)) level = -level; }
                position += run + 1; require(position < 64, "STR AC coefficient exceeds block");
                out.push_back((uint16_t)(run << 10 | ((unsigned)level & 1023)));
            }
        }
        require(out.size() <= 131068, "STR coefficients exceed MDEC command bound");
    }
    if (out.size() & 1) out.push_back(0xfe00);
    return out;
}
VideoDecoder::VideoDecoder() : owner(decoder_mutex)
{
    uint8_t quant[64]; int16_t scale[64];
    for (unsigned i = 0; i < 64; ++i) quant[i] = (uint8_t)tables::default_intra_matrix[scan[i]];
    quant[0] = 2;
    for (unsigned i = 0; i < 64; ++i) {
        const unsigned frequency = i / 8, sample = i % 8;
        const double value = frequency ? std::cos((2 * sample + 1) * frequency * 3.14159265358979323846 / 16.0) : 1 / std::sqrt(2.0);
        scale[i] = (int16_t)std::clamp((int)std::lround(32768 * value), -32768, 32767);
    }
    nitrogen_mdec_start(quant, scale);
}
VideoDecoder::~VideoDecoder() { nitrogen_mdec_finish(); }
Frame VideoDecoder::decode(const Packet &packet)
{
    const auto rle = decode_vlc(packet);
    const unsigned columns = (packet.width + 15) / 16, rows = (packet.height + 15) / 16;
    std::vector<uint8_t> rgb(columns * rows * 768);
    require(nitrogen_mdec_decode(rle.data(), rle.size(), rgb.data(), rgb.size()) != 0, "Incomplete native MDEC output");
    Frame frame; frame.width = packet.width; frame.height = packet.height; frame.pts = packet.pts();
    frame.argb.resize((size_t)frame.width * frame.height);
    for (unsigned x = 0; x < columns; ++x) for (unsigned y = 0; y < rows; ++y) {
        const uint8_t *block = rgb.data() + (x * rows + y) * 768;
        for (unsigned py = 0; py < 16; ++py) for (unsigned px = 0; px < 16; ++px) {
            const unsigned dx = x * 16 + px, dy = y * 16 + py;
            if (dx >= frame.width || dy >= frame.height) continue;
            const uint8_t *p = block + (py * 16 + px) * 3;
            frame.argb[(size_t)dy * frame.width + dx] = 0xff000000u | (uint32_t)p[0] << 16 | (uint32_t)p[1] << 8 | p[2];
        }
    }
    return frame;
}
std::vector<int16_t> XaDecoder::decode(const uint8_t *sector, size_t bytes)
{
    require(bytes == 2352 && (sector[18] & 4) && (sector[19] == 1 || sector[19] == 5), "Unsupported XA audio sector");
    static const int positive[4] = {0,60,115,98}, negative[4] = {0,0,-52,-55};
    std::vector<int16_t> pcm; pcm.reserve(4032);
    for (unsigned group = 0; group < 18; ++group) {
        const uint8_t *data = sector + 24 + group * 128;
        for (unsigned unit = 0; unit < 4; ++unit) {
            int shift[2], filter[2];
            for (unsigned side = 0; side < 2; ++side) {
                const unsigned parameter = data[4 + unit * 2 + side];
                require((parameter & 15) <= 12 && (parameter >> 4) < 4, "Invalid XA ADPCM parameter");
                shift[side] = 12 - (parameter & 15); filter[side] = parameter >> 4;
            }
            for (unsigned sample = 0; sample < 28; ++sample) {
                unsigned packed = data[16 + unit + sample * 4];
                for (unsigned side = 0; side < 2; ++side) {
                    int value = packed >> (side * 4) & 15; if (value >= 8) value -= 16;
                    value = value * (1 << shift[side]) + floor64(positive[filter[side]] * history[side][0] + negative[filter[side]] * history[side][1] + 32);
                    value = std::clamp(value, -32768, 32767);
                    history[side][1] = history[side][0]; history[side][0] = value;
                    pcm.push_back((int16_t)value);
                }
            }
        }
    }
    return pcm;
}
Clip read_clip(const std::string &bin, uint32_t lba, uint32_t sectors, unsigned channel)
{
    require(sectors > 0 && sectors <= 150 * 120 && channel < 32, "Invalid native movie extent");
    std::ifstream input(bin, std::ios::binary); require(input.good(), "Cannot open native movie disc");
    input.seekg((uint64_t)lba * 2352);
    Clip clip; XaDecoder xa;
    Packet pending; std::vector<bool> received; unsigned chunks = 0, completed = 0;
    std::array<uint8_t,2352> raw{};
    for (unsigned sector = 0; sector < sectors; ++sector) {
        input.read((char *)raw.data(), raw.size()); require(input.gcount() == (std::streamsize)raw.size(), "Truncated native movie extent");
        require(raw[0] == 0 && raw[11] == 0 && raw[15] == 2 && std::memcmp(raw.data()+16,raw.data()+20,4)==0, "Invalid movie sector header");
        if ((raw[18] & 4) && raw[16] == 1 && raw[17] == channel) {
            const unsigned rate = raw[19] & 4 ? 18900 : 37800;
            if (!clip.audio.empty()) require(clip.sample_rate == rate, "XA rate changes inside movie");
            clip.sample_rate = rate; auto samples = xa.decode(raw.data(), raw.size());
            const size_t start = (uint64_t)sector * rate / 150;
            if (clip.audio.size() / 2 < start) clip.audio.resize(start * 2, 0);
            clip.audio.insert(clip.audio.end(), samples.begin(), samples.end());
        }
        if (u32(raw.data()+24) != 0x80010160u) continue;
        const unsigned chunk = u16(raw.data()+28), count = u16(raw.data()+30);
        const unsigned number = u32(raw.data()+32), size = u32(raw.data()+36);
        const unsigned width = u16(raw.data()+40), height = u16(raw.data()+42);
        require(count > 0 && count <= 512 && chunk < count && size >= 8 && size <= count * 2016 && size <= 1024*1024, "Invalid STR chunk bounds");
        require(width && width <= 640 && height && height <= 480, "Invalid STR frame dimensions");
        if (received.empty()) {
            pending = Packet{}; pending.number = number; pending.width = width; pending.height = height;
            pending.bytes.resize(size); received.assign(count, false); chunks = count; completed = 0;
        }
        require(number == pending.number && width == pending.width && height == pending.height && size == pending.bytes.size() && count == chunks && !received[chunk], "Inconsistent or repeated STR chunk");
        const size_t offset = (size_t)chunk * 2016;
        // Some authored ending packets include padding-only chunks.
        if (offset < size) std::memcpy(pending.bytes.data()+offset, raw.data()+56, std::min<size_t>(2016,size-offset));
        received[chunk] = true; completed++; pending.end_sector = sector;
        if (completed == chunks) { clip.video.push_back(std::move(pending)); received.clear(); }
    }
    require(received.empty() && !clip.video.empty() && !clip.audio.empty(), "Incomplete native movie stream");
    clip.duration = std::max(clip.video.back().pts() + 1.0/150, clip.audio.size() / (2.0 * clip.sample_rate));
    return clip;
}
}
