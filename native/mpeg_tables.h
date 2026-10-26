/*
 * MPEG-1/2 tables
 * copyright (c) 2000,2001 Fabrice Bellard
 * copyright (c) 2002-2004 Michael Niedermayer <michaelni@gmx.at>
 *
 * This file is part of FFmpeg.
 *
 * FFmpeg is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * FFmpeg is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with FFmpeg; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
 */
// Adapted from FFmpeg n7.1 libavcodec/mpeg12data.c; tables only.
#pragma once
#include <cstdint>
namespace nitrogen::media::tables {
static const uint16_t default_intra_matrix[256] = {
        8, 16, 19, 22, 26, 27, 29, 34,
        16, 16, 22, 24, 27, 29, 34, 37,
        19, 22, 26, 27, 29, 34, 34, 38,
        22, 22, 26, 27, 29, 34, 37, 40,
        22, 26, 27, 29, 32, 35, 40, 48,
        26, 27, 29, 32, 35, 40, 48, 58,
        26, 27, 29, 34, 38, 46, 56, 69,
        27, 29, 35, 38, 46, 56, 69, 83
};
static const uint16_t vlc_dc_lum_code[12] = {
    0x4, 0x0, 0x1, 0x5, 0…2940 tokens truncated…                }
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
