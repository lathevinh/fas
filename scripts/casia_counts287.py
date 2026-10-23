"""Strict native MPEG4 coded-picture versus AVI timing-sample accounting."""

import hashlib


class CountFailure(ValueError):
    pass


class Bits:
    def __init__(self, data):
        self.data, self.position = data, 0

    def take(self, count):
        if self.position + count > len(self.data) * 8:
            raise CountFailure("truncated_codec_header")
        value = 0
        for _ in range(count):
            value = (value << 1) | ((self.data[self.position // 8] >> (7 - self.position % 8)) & 1)
            self.position += 1
        return value


def extradata(stream):
    try:
        encoded = "".join(line.split(":", 1)[1].strip().split("  ", 1)[0].replace(" ", "")
                          for line in stream["extradata"].strip().splitlines())
        result = bytes.fromhex(encoded)
        if not result or len(result) > 65536 or ("extradata_size" in stream and len(result) != stream["extradata_size"]):
            raise CountFailure("codec_extradata_size_mismatch")
        return result
    except (KeyError, IndexError, TypeError, ValueError) as error:
        if isinstance(error, CountFailure):
            raise
        raise CountFailure("invalid_codec_extradata") from error


def resolution(header):
    positions = [index for index in range(len(header) - 3)
                 if header[index:index + 3] == b"\x00\x00\x01" and 0x20 <= header[index + 3] <= 0x2f]
    if len(positions) != 1:
        raise CountFailure("one_native_vol_header_required")
    bits = Bits(header[positions[0] + 4:])
    bits.take(1)
    bits.take(8)
    if bits.take(1):
        bits.take(4)
        bits.take(3)
    aspect = bits.take(4)
    if aspect == 15:
        bits.take(16)
    if bits.take(1):
        bits.take(2)
        bits.take(1)
        if bits.take(1):
            raise CountFailure("unsupported_vbv_header")
    if bits.take(2) != 0 or bits.take(1) != 1:
        raise CountFailure("unsupported_vol_shape_or_marker")
    value = bits.take(16)
    if value <= 0 or bits.take(1) != 1:
        raise CountFailure("invalid_vol_clock")
    return value


def coded_vop(header, clock):
    if header[:4] != b"\x00\x00\x01\xb6":
        raise CountFailure("native_vop_start_required")
    bits = Bits(header[4:])
    bits.take(2)
    while bits.take(1):
        if bits.position > 256:
            raise CountFailure("vop_time_base_cap")
    if bits.take(1) != 1:
        raise CountFailure("invalid_vop_marker")
    if bits.take(max(1, (clock - 1).bit_length())) >= clock or bits.take(1) != 1:
        raise CountFailure("invalid_vop_increment_or_marker")
    return bool(bits.take(1))


def validate(raw, packets, evidence):
    stream, frames = raw["streams"][0], raw["frames"]
    if raw["format"]["format_name"] != "avi" or stream["codec_name"] != "mpeg4":
        raise CountFailure("only_native_avi_mpeg4_count_reconciliation")
    header = extradata(stream)
    clock = resolution(header)
    if evidence["codec_extradata_hex"] != header.hex() or evidence["vol_time_increment_resolution"] != clock:
        raise CountFailure("native_vol_evidence_drift")
    rows, native = evidence["packets"], packets["packets"]
    declared = int(stream["nb_frames"])
    if len(rows) != len(native) or len(rows) != declared:
        raise CountFailure("declared_native_packet_count_mismatch")
    coded, noncoded, seen = set(), [], set()
    for row, packet in zip(rows, native, strict=True):
        identity = (int(packet["pos"]), int(packet["size"]), int(packet["dts"]))
        if identity != (row["pos"], row["size"], row["dts"]) or row["pos"] in seen:
            raise CountFailure("native_packet_identity_drift")
        if row["pos"] < 0 or row["size"] <= 0 or row["pos"] + row["size"] > evidence["source_bytes"]:
            raise CountFailure("native_packet_byte_bounds")
        seen.add(row["pos"])
        vop_header = bytes.fromhex(row["vop_header_hex"])
        if row["vop_offset"] < 0 or row["vop_offset"] + len(vop_header) > row["size"]:
            raise CountFailure("native_vop_header_bounds")
        is_coded = coded_vop(vop_header, clock)
        if is_coded != row["vop_coded"]:
            raise CountFailure("native_vop_flag_drift")
        if is_coded:
            coded.add(row["pos"])
        else:
            if row["size"] > 16 or row["vop_offset"] != 0 or len(vop_header) != row["size"]:
                raise CountFailure("unsupported_non_coded_packet")
            noncoded.append(row["dts"])
    frame_positions = [int(frame["pkt_pos"]) for frame in frames]
    if len(set(frame_positions)) != len(frames) or set(frame_positions) != coded:
        raise CountFailure("every_coded_packet_must_join_exactly_one_decoded_picture")
    if not noncoded or declared != len(frames) + len(noncoded):
        raise CountFailure("unreconciled_declared_picture_count")
    return {"declared_timing_samples": declared, "native_packets": len(rows), "decoded_pictures": len(frames),
            "explicit_non_coded_vops": len(noncoded), "non_coded_vop_native_dts": noncoded,
            "all_declared_samples_accounted": True}


def build(path, raw, packets):
    if path.stat().st_size > 5052628:
        raise CountFailure("canonical_original_byte_cap")
    data = path.read_bytes()
    header = extradata(raw["streams"][0])
    clock = resolution(header)
    rows = []
    for packet in packets["packets"]:
        pos, size = int(packet["pos"]), int(packet["size"])
        if pos < 0 or size <= 0 or pos + size > len(data):
            raise CountFailure("native_packet_byte_bounds")
        payload = data[pos:pos + size]
        start = payload.find(b"\x00\x00\x01\xb6")
        if start < 0 or payload.find(b"\x00\x00\x01\xb6", start + 4) >= 0:
            raise CountFailure("one_vop_per_native_packet_required")
        vop = payload[start:start + 40]
        rows.append({"pos": pos, "size": size, "dts": int(packet["dts"]), "vop_offset": start,
                     "vop_header_hex": vop.hex(), "vop_coded": coded_vop(vop, clock),
                     "packet_sha256": hashlib.sha256(payload).hexdigest()})
    evidence = {"source_sha256": hashlib.sha256(data).hexdigest(), "source_bytes": len(data),
                "codec_extradata_hex": header.hex(), "vol_time_increment_resolution": clock, "packets": rows}
    validate(raw, packets, evidence)
    return evidence
