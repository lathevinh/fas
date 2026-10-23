"""Bounded RAR5 header/CRC commitments; decompression remains with libarchive.

Field layout: https://www.rarlab.com/technote.htm
"""

from __future__ import annotations

import io
from pathlib import Path
import struct
import zlib


def _vint(source, *, maximum_bytes=10):
    value, raw = 0, bytearray()
    for index in range(maximum_bytes):
        byte = source.read(1)
        if not byte:
            raise ValueError("truncated RAR5 variable integer")
        raw.extend(byte)
        value |= (byte[0] & 0x7f) << (index * 7)
        if byte[0] < 0x80:
            if value > 2 ** 64 - 1:
                raise ValueError("RAR5 integer exceeds64bits")
            return value, bytes(raw)
    raise ValueError("RAR5 variable integer byte cap")


def _exact(source, size):
    data = source.read(size)
    if len(data) != size:
        raise ValueError("truncated RAR5 header field")
    return data


def read_file_headers(path: Path):
    """Read bounded headers, never decode or hash a compressed payload."""
    rows, seen, main_seen, end_seen = [], set(), False, False
    with path.open("rb") as source:
        total = path.stat().st_size
        if _exact(source, 8) != b"Rar!\x1a\x07\x01\x00":
            raise ValueError("only the supplied RAR5 container is supported")
        while source.tell() < total:
            expected_crc = struct.unpack("<I", _exact(source, 4))[0]
            header_size, encoded_size = _vint(source, maximum_bytes=3)
            if header_size < 2 or header_size > 2 * 1024 ** 2:
                raise ValueError("RAR5 header byte cap")
            data = _exact(source, header_size)
            if zlib.crc32(encoded_size + data) != expected_crc:
                raise ValueError("RAR5 header CRC mismatch")
            header = io.BytesIO(data)
            kind = _vint(header)[0]
            flags = _vint(header)[0]
            extra_size = _vint(header)[0] if flags & 1 else 0
            packed_size = _vint(header)[0] if flags & 2 else 0
            if flags & 0x18 or extra_size > header_size - header.tell() or packed_size > total - source.tell():
                raise ValueError("split/multivolume or invalid RAR5 bounds")
            content_end = header_size - extra_size
            if kind == 1:
                archive_flags = _vint(header)[0]
                if main_seen or archive_flags & 3:
                    raise ValueError("one non-volume RAR5 main header required")
                main_seen = True
            elif kind in (2, 3):
                if not main_seen:
                    raise ValueError("file before RAR5 main header")
                file_flags = _vint(header)[0]
                unpacked_size = _vint(header)[0]
                attributes = _vint(header)[0]
                if file_flags & 8:
                    raise ValueError("unknown RAR5 unpacked size")
                if file_flags & 2:
                    _exact(header, 4)
                crc = struct.unpack("<I", _exact(header, 4))[0] if file_flags & 4 else None
                compression = _vint(header)[0]
                host = _vint(header)[0]
                name_size = _vint(header)[0]
                if name_size > content_end - header.tell():
                    raise ValueError("RAR5 name exceeds header bounds")
                name = _exact(header, name_size).decode("utf-8")
                if header.tell() != content_end:
                    raise ValueError("unexpected RAR5 file header fields")
                while header.tell() < header_size:
                    size = _vint(header)[0]
                    end = header.tell() + size
                    if size < 1 or end > header_size:
                        raise ValueError("invalid RAR5 extra record bounds")
                    extra_type = _vint(header)[0]
                    if header.tell() > end:
                        raise ValueError("RAR5 extra type exceeds record bounds")
                    if extra_type in {1, 5}:
                        raise ValueError("encrypted or redirected RAR5 member")
                    header.seek(end)
                if kind == 2:
                    directory = bool(file_flags & 1)
                    relative = Path(name)
                    if not name or relative.is_absolute() or ".." in relative.parts or relative.as_posix() != name or "\\" in name or name in seen:
                        raise ValueError("unsafe/duplicate RAR5 member")
                    if host not in {0, 1} or (host == 1 and attributes & 0o170000 not in {0o040000, 0o100000}):
                        raise ValueError("unsupported RAR5 filesystem object")
                    if not directory and crc is None:
                        raise ValueError("regular RAR5 member lacks required unpacked CRC32")
                    if directory and (unpacked_size or packed_size):
                        raise ValueError("RAR5 directory has data payload")
                    seen.add(name)
                    rows.append({"relpath": name, "byte_size": unpacked_size,
                                 "kind": "directory" if directory else "file", "encrypted": False,
                                 "crc32": crc, "packed_size": packed_size, "compression": compression})
            elif kind == 4:
                raise ValueError("encrypted RAR5 headers unsupported")
            elif kind == 5:
                if not main_seen or _vint(header)[0] != 0 or packed_size:
                    raise ValueError("RAR5 continuation/end mismatch")
                end_seen = True
                if source.tell() != total:
                    raise ValueError("unexpected bytes after RAR5 end")
                break
            else:
                raise ValueError("unknown RAR5 header type")
            source.seek(packed_size, io.SEEK_CUR)
        if not main_seen or not end_seen or not rows:
            raise ValueError("incomplete RAR5 header sequence")
    return rows
