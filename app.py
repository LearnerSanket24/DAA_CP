from __future__ import annotations

import io
import os
import tempfile
import time
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

from algorithms.huffman import HuffmanError, compress, decompress, inspect


MAX_UPLOAD_BYTES = 16 * 1024 * 1024
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES + 1024 * 1024
DOWNLOADS: dict[str, tuple[bytes, str, str]] = {}


def _error(message: str, status: int = 400):
    return jsonify({"error": message}), status


def _uploaded_file():
    uploaded = request.files.get("file")
    if uploaded is None or not uploaded.filename:
        raise ValueError("Choose a file before continuing.")
    data = uploaded.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise ValueError(f"Files must be {MAX_UPLOAD_BYTES // (1024 * 1024)} MB or smaller.")
    return uploaded.filename, data


def _store_download(data: bytes, filename: str, mimetype: str) -> str:
    token = uuid.uuid4().hex
    DOWNLOADS[token] = (data, filename, mimetype)
    return f"/download/{token}"


@app.get("/")
def index():
    return render_template("index.html", max_upload_mb=MAX_UPLOAD_BYTES // (1024 * 1024))


@app.post("/api/compress")
def api_compress():
    try:
        filename, data = _uploaded_file()
        started = time.perf_counter()
        result = compress(data)
        elapsed_ms = (time.perf_counter() - started) * 1000
        output_name = f"{Path(secure_filename(filename)).stem or 'file'}.huff"
        payload = {
            "operation": "compression",
            "filename": filename,
            "download_url": _store_download(result.data, output_name, "application/octet-stream"),
            "original_size": len(data),
            "compressed_size": len(result.data),
            "compression_ratio": result.compression_ratio,
            "space_savings": result.space_savings,
            "elapsed_ms": round(elapsed_ms, 3),
            "distinct_symbols": len(result.frequencies),
            "codes": result.codes_for_display(),
            "tree": result.tree_for_display(),
            "integrity_verified": True,
        }
        return jsonify(payload)
    except (ValueError, HuffmanError) as exc:
        return _error(str(exc))


@app.post("/api/decompress")
def api_decompress():
    try:
        filename, data = _uploaded_file()
        started = time.perf_counter()
        restored = decompress(data)
        elapsed_ms = (time.perf_counter() - started) * 1000
        stem = Path(secure_filename(filename)).stem or "restored"
        if stem.endswith(".huff"):
            stem = stem[:-5]
        payload = {
            "operation": "decompression",
            "filename": filename,
            "download_url": _store_download(restored, f"{stem}.restored", "application/octet-stream"),
            "restored_size": len(restored),
            "elapsed_ms": round(elapsed_ms, 3),
            "integrity_verified": True,
        }
        return jsonify(payload)
    except (ValueError, HuffmanError) as exc:
        return _error(str(exc))


@app.post("/api/inspect")
def api_inspect():
    try:
        _, data = _uploaded_file()
        return jsonify(inspect(data))
    except (ValueError, HuffmanError) as exc:
        return _error(str(exc))


@app.post("/api/benchmark")
def api_benchmark():
    try:
        filename, data = _uploaded_file()
        started = time.perf_counter()
        result = compress(data)
        compression_ms = (time.perf_counter() - started) * 1000
        started = time.perf_counter()
        restored = decompress(result.data)
        decompression_ms = (time.perf_counter() - started) * 1000
        return jsonify(
            {
                "filename": filename,
                "original_size": len(data),
                "compressed_size": len(result.data),
                "compression_ratio": result.compression_ratio,
                "space_savings": result.space_savings,
                "compression_ms": round(compression_ms, 3),
                "decompression_ms": round(decompression_ms, 3),
                "integrity_verified": restored == data,
            }
        )
    except (ValueError, HuffmanError) as exc:
        return _error(str(exc))


@app.get("/download/<token>")
def download(token: str):
    stored = DOWNLOADS.get(token)
    if stored is None:
        return _error("This download has expired or does not exist.", 404)
    data, filename, mimetype = stored
    return send_file(io.BytesIO(data), as_attachment=True, download_name=filename, mimetype=mimetype)


@app.errorhandler(413)
def too_large(_error):
    return _error(f"Files must be {MAX_UPLOAD_BYTES // (1024 * 1024)} MB or smaller.", 413)


if __name__ == "__main__":
    app.run(debug=True)
