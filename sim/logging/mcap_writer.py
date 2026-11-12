"""Minimal MCAP writer (MCAP format version 0, https://mcap.dev/spec), standard library only.

Unchunked, uncompressed: magic, Header, Schema/Channel/Message/Metadata records, DataEnd,
then a summary section (Schema, Channel, Statistics) and the Footer. Messages are JSON with
a JSON Schema, which Foxglove reads directly. CRC fields are 0 ("not computed"), as the
specification allows.
"""

import json
import struct
from pathlib import Path
from typing import BinaryIO

MAGIC = b"\x89MCAP0\r\n"
OP_HEADER, OP_FOOTER, OP_SCHEMA, OP_CHANNEL, OP_MESSAGE = 0x01, 0x02, 0x03, 0x04, 0x05
OP_STATISTICS, OP_METADATA, OP_DATA_END = 0x0B, 0x0C, 0x0F


def _string(text: str) -> bytes:
    data = text.encode("utf-8")
    return struct.pack("<I", len(data)) + data


def _map(items: dict[str, str]) -> bytes:
    body = b"".join(_string(k) + _string(v) for k, v in items.items())
    return struct.pack("<I", len(body)) + body


def _bytes(data: bytes) -> bytes:
    return struct.pack("<I", len(data)) + data


def _record(op: int, content: bytes) -> bytes:
    return struct.pack("<BQ", op, len(content)) + content


def json_schema_of(sample) -> dict:
    """JSON Schema of one sample message, so that viewers list its fields."""
    if isinstance(sample, bool):
        return {"type": "boolean"}
    if isinstance(sample, (int, float)):
        return {"type": "number"}
    if isinstance(sample, str):
        return {"type": "string"}
    if isinstance(sample, (list, tuple)):
        return {"type": "array", "items": json_schema_of(sample[0]) if sample else {}}
    if isinstance(sample, dict):
        return {"type": "object", "properties": {k: json_schema_of(v) for k, v in sample.items()}}
    return {}


class McapWriter:
    """Write JSON messages on named topics; call close() (or use as a context manager)."""

    def __init__(self, path: Path, profile: str = "") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._f: BinaryIO = open(self.path, "wb")
        self._f.write(MAGIC)
        self._f.write(_record(OP_HEADER, _string(profile) + _string("pp sim.logging")))
        self._schemas: list[bytes] = []
        self._channels: dict[str, tuple[int, bytes]] = {}
        self._counts: dict[int, int] = {}
        self._start: int | None = None
        self._end = 0
        self._metadata = 0

    def _channel(self, topic: str, sample: dict) -> int:
        if topic not in self._channels:
            schema_id = len(self._schemas) + 1
            schema = _record(OP_SCHEMA, struct.pack("<H", schema_id) + _string(topic.strip("/").replace("/", ".")) +
                             _string("jsonschema") + _bytes(json.dumps(json_schema_of(sample)).encode()))
            channel_id = len(self._channels) + 1
            channel = _record(OP_CHANNEL, struct.pack("<HH", channel_id, schema_id) + _string(topic) +
                              _string("json") + _map({}))
            self._f.write(schema)
            self._f.write(channel)
            self._schemas.append(schema)
            self._channels[topic] = (channel_id, channel)
            self._counts[channel_id] = 0
        return self._channels[topic][0]

    def message(self, topic: str, time_ns: int, data: dict) -> None:
        channel_id = self._channel(topic, data)
        sequence = self._counts[channel_id]
        self._counts[channel_id] = sequence + 1
        payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        self._f.write(_record(OP_MESSAGE, struct.pack("<HIQQ", channel_id, sequence, time_ns, time_ns) + payload))
        self._start = time_ns if self._start is None else min(self._start, time_ns)
        self._end = max(self._end, time_ns)

    def metadata(self, name: str, values: dict[str, str]) -> None:
        self._f.write(_record(OP_METADATA, _string(name) + _map({k: str(v) for k, v in values.items()})))
        self._metadata += 1

    def close(self) -> Path:
        f = self._f
        f.write(_record(OP_DATA_END, struct.pack("<I", 0)))
        summary_start = f.tell()
        for schema in self._schemas:
            f.write(schema)
        for _, channel in self._channels.values():
            f.write(channel)
        counts = b"".join(struct.pack("<HQ", cid, n) for cid, n in self._counts.items())
        f.write(_record(OP_STATISTICS, struct.pack("<QHIIIIQQ", sum(self._counts.values()), len(self._schemas),
                                                   len(self._channels), 0, self._metadata, 0,
                                                   self._start or 0, self._end)
                        + struct.pack("<I", len(counts)) + counts))
        f.write(_record(OP_FOOTER, struct.pack("<QQI", summary_start, 0, 0)))
        f.write(MAGIC)
        f.close()
        return self.path

    def __enter__(self) -> "McapWriter":
        return self

    def __exit__(self, *exc) -> None:
        if not self._f.closed:
            self.close()


def read(path: Path) -> dict:
    """Parse a file written here (records of the data section); for tests and quick checks."""
    raw = Path(path).read_bytes()
    if not (raw.startswith(MAGIC) and raw.endswith(MAGIC)):
        raise ValueError("not an MCAP file")
    pos, channels, out = len(MAGIC), {}, {"messages": [], "metadata": {}, "ops": []}

    def string(at: int) -> tuple[str, int]:
        (n,) = struct.unpack_from("<I", raw, at)
        return raw[at + 4:at + 4 + n].decode("utf-8"), at + 4 + n

    while pos < len(raw) - len(MAGIC):
        op, length = struct.unpack_from("<BQ", raw, pos)
        body = pos + 9
        out["ops"].append(op)
        if op == OP_CHANNEL:
            cid, _ = struct.unpack_from("<HH", raw, body)
            topic, _ = string(body + 4)
            channels[cid] = topic
        elif op == OP_MESSAGE:
            cid, seq, log_time, _ = struct.unpack_from("<HIQQ", raw, body)
            out["messages"].append((channels[cid], log_time, json.loads(raw[body + 22:body + length])))
        elif op == OP_METADATA:
            name, at = string(body)
            (size,) = struct.unpack_from("<I", raw, at)
            at, end, values = at + 4, at + 4 + size, {}
            while at < end:
                key, at = string(at)
                value, at = string(at)
                values[key] = value
            out["metadata"][name] = values
        elif op == OP_STATISTICS:
            out["message_count"] = struct.unpack_from("<Q", raw, body)[0]
        elif op == OP_FOOTER:
            out["summary_start"] = struct.unpack_from("<Q", raw, body)[0]
        pos = body + length
    return out
