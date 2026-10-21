from __future__ import annotations

import heapq
import struct
from dataclasses import dataclass
from typing import Optional


MAGIC = b"HUF1"
HEADER_FORMAT = ">4sQ"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT) + 256 * 8


class HuffmanError(ValueError):
    """Raised when a Huffman stream is invalid or cannot be decoded."""


@dataclass
class Node:
    frequency: int
    symbol: Optional[int] = None
    left: Optional["Node"] = None
    right: Optional["Node"] = None
    order: int = 0

    @property
    def is_leaf(self) -> bool:
        return self.symbol is not None


@dataclass
class CompressionResult:
    data: bytes
    frequencies: dict[int, int]
    codes: dict[int, str]
    root: Optional[Node]
    original_size: int

    @property
    def compression_ratio(self) -> float:
        return self.original_size / len(self.data) if self.data else 0.0

    @property
    def space_savings(self) -> float:
        if self.original_size == 0:
            return 0.0
        return (self.original_size - len(self.data)) / self.original_size * 100

    def codes_for_display(self) -> list[dict[str, object]]:
        return [
            {"symbol": _symbol_label(symbol), "value": symbol, "frequency": self.frequencies[symbol], "code": code}
            for symbol, code in sorted(self.codes.items())
        ]

    def tree_for_display(self) -> Optional[dict[str, object]]:
        return _tree_to_dict(self.root)


def _symbol_label(symbol: int) -> str:
    if 32 <= symbol <= 126:
        return repr(chr(symbol))
    return f"0x{symbol:02X}"


def _frequencies(data: bytes) -> dict[int, int]:
    counts = [0] * 256
    for value in data:
        counts[value] += 1
    return {symbol: count for symbol, count in enumerate(counts) if count}


def build_tree(frequencies: dict[int, int]) -> Optional[Node]:
    if not frequencies:
        return None
    heap: list[tuple[int, int, Node]] = []
    for order, (symbol, frequency) in enumerate(sorted(frequencies.items())):
        heapq.heappush(heap, (frequency, order, Node(frequency, symbol=symbol, order=order)))
    next_order = len(heap)
    while len(heap) > 1:
        left_frequency, _, left = heapq.heappop(heap)
        right_frequency, _, right = heapq.heappop(heap)
        parent = Node(left_frequency + right_frequency, left=left, right=right, order=next_order)
        next_order += 1
        heapq.heappush(heap, (parent.frequency, parent.order, parent))
    return heap[0][2]


def generate_codes(root: Optional[Node]) -> dict[int, str]:
    if root is None:
        return {}
    if root.is_leaf:
        return {root.symbol: "0"}  # type: ignore[index]
    codes: dict[int, str] = {}

    def visit(node: Node, prefix: str) -> None:
        if node.is_leaf:
            codes[node.symbol] = prefix  # type: ignore[index]
            return
        if node.left is not None:
            visit(node.left, prefix + "0")
        if node.right is not None:
            visit(node.right, prefix + "1")

    visit(root, "")
    return codes


def compress(data: bytes) -> CompressionResult:
    frequencies = _frequencies(data)
    root = build_tree(frequencies)
    codes = generate_codes(root)
    payload = bytearray()
    current = 0
    bit_count = 0
    for value in data:
        for bit in codes[value]:
            current = (current << 1) | (bit == "1")
            bit_count += 1
            if bit_count == 8:
                payload.append(current)
                current = 0
                bit_count = 0
    if bit_count:
        payload.append(current << (8 - bit_count))
    header = struct.pack(HEADER_FORMAT, MAGIC, len(data))
    header += b"".join(struct.pack(">Q", frequencies.get(symbol, 0)) for symbol in range(256))
    return CompressionResult(header + payload, frequencies, codes, root, len(data))


def _read_header(data: bytes) -> tuple[int, dict[int, int], bytes]:
    if len(data) < HEADER_SIZE or data[:4] != MAGIC:
        raise HuffmanError("The file is not a valid Huffman stream.")
    _, original_size = struct.unpack(HEADER_FORMAT, data[: struct.calcsize(HEADER_FORMAT)])
    frequencies: dict[int, int] = {}
    offset = struct.calcsize(HEADER_FORMAT)
    for symbol in range(256):
        frequency = struct.unpack(">Q", data[offset : offset + 8])[0]
        offset += 8
        if frequency:
            frequencies[symbol] = frequency
    if sum(frequencies.values()) != original_size:
        raise HuffmanError("The compressed header contains inconsistent size information.")
    return original_size, frequencies, data[HEADER_SIZE:]


def decompress(data: bytes) -> bytes:
    original_size, frequencies, payload = _read_header(data)
    if original_size == 0:
        if payload:
            raise HuffmanError("Empty streams must not contain encoded payload data.")
        return b""
    root = build_tree(frequencies)
    if root is None:
        raise HuffmanError("The compressed stream has no decoding tree.")
    codes = generate_codes(root)
    expected_bits = sum(frequencies[symbol] * len(code) for symbol, code in codes.items())
    expected_payload_size = (expected_bits + 7) // 8
    if len(payload) != expected_payload_size:
        raise HuffmanError("The compressed payload length does not match its header.")
    padding_bits = expected_payload_size * 8 - expected_bits
    if padding_bits and payload[-1] & ((1 << padding_bits) - 1):
        raise HuffmanError("The compressed payload contains invalid padding bits.")
    if root.is_leaf:
        return bytes([root.symbol]) * original_size  # type: ignore[list-item]
    output = bytearray()
    node = root
    for value in payload:
        for shift in range(7, -1, -1):
            node = node.right if ((value >> shift) & 1) else node.left
            if node is None:
                raise HuffmanError("The compressed payload is corrupt.")
            if node.is_leaf:
                output.append(node.symbol)  # type: ignore[arg-type]
                if len(output) == original_size:
                    return bytes(output)
                node = root
    raise HuffmanError("The compressed payload ended before the original data was restored.")


def inspect(data: bytes) -> dict[str, object]:
    result = compress(data)
    return {
        "original_size": len(data),
        "distinct_symbols": len(result.frequencies),
        "frequencies": result.codes_for_display(),
        "tree": result.tree_for_display(),
    }


def _tree_to_dict(node: Optional[Node]) -> Optional[dict[str, object]]:
    if node is None:
        return None
    if node.is_leaf:
        return {"label": _symbol_label(node.symbol), "frequency": node.frequency, "symbol": node.symbol}
    return {
        "label": f"{node.frequency} bytes",
        "frequency": node.frequency,
        "left": _tree_to_dict(node.left),
        "right": _tree_to_dict(node.right),
    }
