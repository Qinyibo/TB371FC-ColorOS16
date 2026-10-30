#!/usr/bin/env python3
"""lp_probe.py —— 离线识别 Android super 镜像（raw 或 sparse）里的逻辑分区布局。

用途：回答"这个 super 镜像里到底装了什么"——每个逻辑分区的名字、大小、
起始扇区，以及该分区头部的文件系统魔数（EROFS / EXT4 / 空）。

只读，不改任何东西。
"""
import json
import struct
import sys

SPARSE_MAGIC = 0xED26FF3A
LP_GEOMETRY_MAGIC = 0x616C4467
LP_HEADER_MAGIC = 0x414C5030
CHUNK_TYPE_RAW = 0xCAC1
CHUNK_TYPE_FILL = 0xCAC2
CHUNK_TYPE_DONT_CARE = 0xCAC3
CHUNK_TYPE_CRC32 = 0xCAC4


class SparseReader:
    """把 Android sparse 镜像映射成可随机读的字节视图（只解析头部建立的块表）。"""

    def __init__(self, fh, verbose=True):
        self.fh = fh
        fh.seek(0)
        hdr = fh.read(28)
        magic, major, minor, file_hdr_sz, chunk_hdr_sz, blk_sz, total_blks, total_chunks, _csum = struct.unpack(
            "<IHHHHIIII", hdr)
        if magic != SPARSE_MAGIC:
            raise ValueError("not sparse")
        self.blk_sz = blk_sz
        self.total_blks = total_blks
        self.total_chunks = total_chunks
        self.chunks = []  # (out_blk_start, n_blks, type, data_offset, fill)
        fh.seek(file_hdr_sz)
        out_blk = 0
        for _ in range(total_chunks):
            ch = fh.read(chunk_hdr_sz)
            ctype, _res, cblks, csz = struct.unpack("<HHII", ch[:12])
            data_off = fh.tell()
            data_len = csz - chunk_hdr_sz
            self.chunks.append((out_blk, cblks, ctype, data_off, data_len))
            out_blk += cblks
            fh.seek(data_off + data_len)
        if verbose:
            print(f"  [sparse] blk_sz={blk_sz} total_blks={total_blks} chunks={total_chunks} "
                  f"=> 展开后 {total_blks * blk_sz} 字节")

    def read_range(self, offset, length, chunk_limit=64):
        """读取展开后的 [offset, offset+length)。只支持落在前 chunk_limit 个 chunk 内的读取。"""
        blk = self.blk_sz
        start_blk = offset // blk
        end_blk = (offset + length + blk - 1) // blk
        out = bytearray((end_blk - start_blk) * blk)
        hit = 0
        for i, (ob, n, ctype, doff, dlen) in enumerate(self.chunks):
            if i >= chunk_limit:
                break
            c_start, c_end = ob, ob + n
            if c_end <= start_blk or c_start >= end_blk:
                continue
            hit += 1
            a = max(c_start, start_blk)
            b = min(c_end, end_blk)
            tgt = (a - start_blk) * blk
            nbytes = (b - a) * blk
            if ctype == CHUNK_TYPE_RAW:
                self.fh.seek(doff + (a - c_start) * blk)
                out[tgt:tgt + nbytes] = self.fh.read(nbytes)
            elif ctype == CHUNK_TYPE_FILL:
                self.fh.seek(doff)
                fill = self.fh.read(4)
                out[tgt:tgt + nbytes] = fill * (nbytes // 4)
            # DONT_CARE / CRC32 保持 0
        return bytes(out)[offset - start_blk * blk: offset - start_blk * blk + length]


def parse_geometry(buf):
    """LpMetadataGeometry: magic(4) struct_size(4) checksum(32) max_size(4) slots(4) lblk(4)。"""
    for off in (4096, 0, 8192):
        if off + 52 <= len(buf) and struct.unpack_from("<I", buf, off)[0] == LP_GEOMETRY_MAGIC:
            struct_size = struct.unpack_from("<I", buf, off + 4)[0]
            meta_max, slot_count, lblk = struct.unpack_from("<III", buf, off + 40)
            return {"geom_offset": off, "struct_size": struct_size, "metadata_max_size": meta_max,
                    "metadata_slot_count": slot_count, "logical_block_size": lblk}
    return None


def parse_metadata(buf, geom):
    """在 geometry 之后寻找 LpMetadataHeader。返回分区列表。"""
    base = geom["geom_offset"] + 4096
    max_size = geom["metadata_max_size"]
    region = buf[base: base + max_size] if base + max_size <= len(buf) else buf[base:]
    hdr_off = None
    for off in range(0, max(0, len(region) - 128), 4):
        if struct.unpack_from("<I", region, off)[0] == LP_HEADER_MAGIC:
            hdr_off = off
            break
    if hdr_off is None:
        return None
    # LpMetadataHeader (v1.0, header_size=128):
    #   magic(4) major(2) minor(2) header_size(4) header_checksum(32) tables_size(4)
    #   tables_checksum(32) partitions(12) extents(12) groups(12) block_devices(12)
    # 四个表描述符固定在 header+80/+92/+104/+116，表数据从 header+header_size 开始。
    major, minor, header_size = struct.unpack_from("<HHI", region, hdr_off + 4)
    tables_size = struct.unpack_from("<I", region, hdr_off + 44)[0]
    tables_off = hdr_off + header_size
    tables = region[tables_off: tables_off + tables_size]

    def table(i):
        return struct.unpack_from("<III", region, hdr_off + 80 + i * 12)

    p_off, p_num, p_esz = table(0)
    e_off, e_num, e_esz = table(1)
    g_off, g_num, g_esz = table(2)

    groups = []
    for i in range(g_num):
        name = tables[g_off + i * g_esz: g_off + i * g_esz + 36].split(b"\0")[0].decode("utf-8", "replace")
        groups.append(name)

    extents = []
    for i in range(e_num):
        num_sectors, target_type, target_data, target_source = struct.unpack_from(
            "<QIQI", tables, e_off + i * e_esz)
        extents.append({"sectors": num_sectors, "type": target_type,
                        "target_data": target_data, "source": target_source})

    parts = []
    for i in range(p_num):
        rec = tables[p_off + i * p_esz: p_off + (i + 1) * p_esz]
        name = rec[:36].split(b"\0")[0].decode("utf-8", "replace")
        attributes, first_ext, num_ext, group_idx = struct.unpack_from("<IIII", rec, 36)
        exts = extents[first_ext: first_ext + num_ext]
        total_sectors = sum(e["sectors"] for e in exts)
        parts.append({
            "name": name, "attributes": attributes,
            "group": groups[group_idx] if group_idx < len(groups) else str(group_idx),
            "extents": exts,
            "size_bytes": total_sectors * 512,
        })
    return {"header": {"major": major, "minor": minor, "header_size": header_size,
                       "tables_size": tables_size,
                       "metadata_region_offset": base + hdr_off},
            "groups": groups, "partitions": parts}


def fs_magic_at(view, byte_offset):
    """探测某个绝对偏移处的文件系统魔数。view(offset, length) -> bytes"""
    try:
        head = view(byte_offset, 4096)
    except Exception as exc:  # noqa: BLE001
        return f"<读失败: {exc}>"
    if len(head) < 2048:
        return "<越界>"
    if all(b == 0 for b in head[:4096]):
        return "全零(未写入)"
    if struct.unpack_from("<I", head, 1024)[0] == 0xE0F5E1E2:
        return "EROFS"
    if struct.unpack_from("<H", head, 1080)[0] == 0xEF53:
        return "EXT4"
    m = struct.unpack_from("<I", head, 0)[0]
    if m == SPARSE_MAGIC:
        return "Android-sparse"
    if struct.unpack_from("<I", head, 1024)[0] == 0x58465342:
        return "XFS"
    return "未知(%08x)" % struct.unpack_from("<I", head, 0)[0]


def main():
    path = sys.argv[1]
    with open(path, "rb") as fh:
        fh.seek(0)
        first = fh.read(4)
        is_sparse = struct.unpack("<I", first)[0] == SPARSE_MAGIC
        print(f"镜像: {path}")
        print(f"格式: {'Android sparse' if is_sparse else 'raw'}")
        if is_sparse:
            sr = SparseReader(fh)
            view = lambda o, l: sr.read_range(o, l, chunk_limit=256)  # noqa: E731
            head2m = sr.read_range(0, 2 * 1024 * 1024, chunk_limit=256)
        else:
            fh.seek(0)
            head2m = fh.read(2 * 1024 * 1024)
            view = lambda o, l: (fh.seek(o), fh.read(l))[1]  # noqa: E731

        geom = parse_geometry(head2m)
        if not geom:
            print("!! 找不到 LP geometry（不是 liblp super 镜像？）")
            return 1
        print(f"geometry: {geom}")
        md = parse_metadata(head2m, geom)
        if not md:
            print("!! 找不到 LP metadata header")
            return 1
        print(f"metadata: {md['header']}")
        print(f"groups: {md['groups']}")
        print()
        print(f"{'分区':<16}{'大小':>14}  {'组':<28}{'首扇区':>12}  {'文件系统'}")
        print("-" * 92)
        for p in md["partitions"]:
            if not p["extents"]:
                print(f"{p['name']:<16}{0:>14}  {p['group']:<28}{'-':>12}  (无 extent)")
                continue
            first_ext = p["extents"][0]
            byte_off = first_ext["target_data"] * 512
            mag = fs_magic_at(view, byte_off)
            size_mb = p["size_bytes"] / 1024 / 1024
            print(f"{p['name']:<16}{size_mb:>11.1f} MB  {p['group']:<28}{first_ext['target_data']:>12}  {mag}")
            if len(p["extents"]) > 1:
                print(f"{'':<16}{'  (共 %d 个 extent)' % len(p['extents'])}")
        print()
        used = [e["target_data"] * 512 + e["sectors"] * 512 for p in md["partitions"] for e in p["extents"]]
        if used:
            print(f"最高被占用的字节偏移: {max(used)} ({max(used)/1024/1024/1024:.2f} GB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
