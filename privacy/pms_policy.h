// SPDX-License-Identifier: Apache-2.0
#pragma once
#include <cstddef>
#include <cstdint>

namespace r94pms {
constexpr size_t kMaxRequest = 10000;
constexpr size_t kMaxReply = 65536;
inline bool allowed_uid(uint32_t uid) { return uid == 0 || uid == 1000; }
inline uint32_t be32(const uint8_t* p) {
    return uint32_t(p[0]) << 24 | uint32_t(p[1]) << 16 | uint32_t(p[2]) << 8 | p[3];
}
// MethodBuffer's second word is a buffer-size constant, never caller identity.
// Reject duplicates, overflow/truncation, trailing data and other PMS namespaces.
inline bool request(const uint8_t* p, size_t n, uint32_t* method) {
    if (!p || n < 12 || n > kMaxRequest) return false;
    const uint32_t cmd = be32(p), count = be32(p + 8);
    if (cmd < 4001 || cmd > 4007 || count == 0 || count > 22) return false;
    bool seen[22] = {}, privacy = false;
    size_t pos = 12;
    for (uint32_t i = 0; i < count; ++i) {
        if (n - pos < 8) return false;
        const uint32_t kind = be32(p + pos), len = be32(p + pos + 4);
        pos += 8;
        if (len > n - pos || kind < 200 || kind > 221 || seen[kind - 200]) return false;
        seen[kind - 200] = true;
        if (kind == 201) {
            if (len != 4 || be32(p + pos) != 1) return false;
            privacy = true;
        }
        pos += len;
    }
    if (!privacy || pos != n) return false;
    *method = cmd;
    return true;
}
// Relay actual backend decisions. Nonzero authentication status is not rewritten.
inline bool response(const uint8_t* p, size_t n, uint32_t method) {
    if (!p || n < 12 || n > kMaxReply || be32(p) != method) return false;
    const uint32_t count = be32(p + 8);
    if (count > 64) return false;
    size_t pos = 12;
    for (uint32_t i = 0; i < count; ++i) {
        if (n - pos < 8) return false;
        const uint32_t len = be32(p + pos + 4);
        pos += 8;
        if (len > n - pos) return false;
        pos += len;
    }
    return pos == n;
}
}
