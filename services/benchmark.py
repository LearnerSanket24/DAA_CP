from __future__ import annotations

import time
from collections.abc import Iterable

from algorithms.huffman import compress, decompress


def benchmark(files: Iterable[tuple[str, bytes]]) -> list[dict[str, object]]:
    results = []
    for filename, data in files:
        started = time.perf_counter()
        compressed = compress(data)
        compression_ms = (time.perf_counter() - started) * 1000
        started = time.perf_counter()
        restored = decompress(compressed.data)
        decompression_ms = (time.perf_counter() - started) * 1000
        results.append(
            {
                "filename": filename,
                "original_size": len(data),
                "compressed_size": len(compressed.data),
                "compression_ratio": compressed.compression_ratio,
                "space_savings": compressed.space_savings,
                "compression_ms": compression_ms,
                "decompression_ms": decompression_ms,
                "integrity_verified": restored == data,
            }
        )
    return results
