from __future__ import annotations

import pytest

from algorithms.huffman import HuffmanError, compress, decompress, generate_codes


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"A",
        b"A" * 1000,
        b"BANANA BANDANA",
        bytes(range(256)) * 4,
        bytes(range(256)),
        bytes([0, 255, 1, 128, 13, 10]) * 17,
    ],
)
def test_round_trip_for_binary_inputs(data: bytes) -> None:
    result = compress(data)
    assert decompress(result.data) == data


def test_codes_are_prefix_free() -> None:
    result = compress(b"the quick brown fox jumps over the lazy dog")
    codes = list(result.codes.values())
    assert all(
        left == right or (not left.startswith(right) and not right.startswith(left))
        for left in codes
        for right in codes
    )


def test_metadata_is_included_in_compressed_size() -> None:
    result = compress(b"small")
    assert len(result.data) > len(b"small")


def test_corrupt_stream_is_rejected() -> None:
    encoded = bytearray(compress(b"this is valid data").data)
    encoded[0] = ord("X")
    with pytest.raises(HuffmanError):
        decompress(bytes(encoded))


def test_truncated_stream_is_rejected() -> None:
    encoded = compress(b"this is valid data").data
    with pytest.raises(HuffmanError):
        decompress(encoded[:-1])


def test_single_symbol_gets_a_decodable_code() -> None:
    result = compress(b"\xff" * 10)
    assert generate_codes(result.root) == {255: "0"}
    assert decompress(result.data) == b"\xff" * 10
