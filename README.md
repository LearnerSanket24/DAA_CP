# 🗜️ Smart File Compression Workbench

<p align="center">
  <strong>Explore • Compress • Measure • Verify</strong><br>
  <em>A colorful DAA project demonstrating Huffman Coding through an interactive web workbench.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/DAA-Greedy%20Algorithm-2563EB?style=for-the-badge" alt="DAA Greedy Algorithm">
  <img src="https://img.shields.io/badge/Algorithm-Huffman%20Coding-0F9F92?style=for-the-badge" alt="Huffman Coding">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge" alt="Python">
  <img src="https://img.shields.io/badge/Flask-Web%20App-111827?style=for-the-badge" alt="Flask">
</p>

<table>
<tr>
<td align="center">📦<br><strong>Lossless</strong><br><sub>Exact byte restoration</sub></td>
<td align="center">🌳<br><strong>Algorithmic</strong><br><sub>Min-heap + tree</sub></td>
<td align="center">📊<br><strong>Analytical</strong><br><sub>Metrics + benchmarks</sub></td>
<td align="center">✅<br><strong>Tested</strong><br><sub>12 automated tests</sub></td>
</tr>
</table>

## 🎓 What is this project?

**Smart File Compression Workbench** is a Flask-based educational application that
implements **Huffman Coding from scratch**. It compresses arbitrary binary files,
restores them without data loss, displays generated prefix codes, and measures
compression performance.

> ⭐ **DAA focus:** The project demonstrates a greedy algorithm, min-priority queue,
> binary tree construction, recursion, bit packing, complexity analysis, and
> empirical performance measurement. It does not rely on `zipfile`, `gzip`, or a
> third-party compression algorithm.

📘 **For the complete teacher explanation, see
[PROJECT_FLOW.md](PROJECT_FLOW.md).** It contains the project flow, implementation
details, complexity analysis, demonstration script, and viva questions.

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 Custom Huffman engine | Frequency counting, min-heap, tree, codes, encoding, and decoding |
| 📁 Binary-file support | Processes every byte from `0` to `255`, not only text |
| 🗜️ Lossless compression | Restores the exact original byte sequence |
| 💾 Self-describing format | `.huff` contains the original size, frequency table, and payload |
| 📊 Performance dashboard | Shows sizes, ratio, savings, and execution time |
| 🔍 Algorithm explorer | Displays symbol frequencies, codes, and tree information |
| 🧪 Reliability checks | Detects invalid headers, corrupted payloads, bad padding, and truncation |
| 📈 Benchmarking | Measures compression, decompression, and integrity status |

## 🔄 Application flow

```mermaid
flowchart LR
    A([📁 Select file]) --> B[🔢 Count frequencies]
    B --> C[⛏️ Build min-heap]
    C --> D[🌳 Build Huffman tree]
    D --> E[🔤 Generate codes]
    E --> F[📦 Encode bits]
    F --> G[(💾 .huff file)]
    G --> H[🔁 Decode + verify]
    H --> I([✅ Restore original])
```

## 🧮 DAA complexity

For `n` input bytes, `k` distinct symbols, and `B` encoded bits:

| Operation | Complexity |
|---|---:|
| Frequency counting | `O(n)` |
| Heap initialization | `O(k)` |
| Huffman tree construction | `O(k log k)` |
| Code generation | `O(k)` |
| Encoding | `O(n + B)` |
| Decoding | `O(B)` |
| Auxiliary algorithmic space | `O(k)` |

Because this implementation uses a byte alphabet, `k ≤ 256`.

## 📈 Metrics

Let `Sₒ` be the original size and `S꜀` be the complete `.huff` size, including
metadata:

```text
Compression ratio = Sₒ / S꜀
Space savings     = ((Sₒ - S꜀) / Sₒ) × 100
```

> ⚠️ Small files or already-compressed files may become larger because the
> self-describing format includes a frequency-table header. This is an important
> experimental result, not an error.

## 🗂️ Project structure

```text
DAA_CP/
├── algorithms/
│   └── huffman.py       # Core Huffman algorithm
├── services/
│   └── benchmark.py     # Timing and integrity benchmarks
├── static/
│   ├── app.js           # Frontend behavior
│   └── style.css        # Dashboard styling
├── templates/
│   └── index.html       # Web interface
├── tests/
│   └── test_huffman.py  # Automated correctness tests
├── app.py               # Flask server and API routes
├── PROJECT_FLOW.md      # Detailed teacher/viva explanation
└── requirements.txt     # Python dependencies
```

## 🚀 Run on Windows

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000** in a browser.

Run the automated tests:

```powershell
python -m pytest -q
```

Expected result:

```text
12 passed
```

## 🔌 API routes

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/` | Open the dashboard |
| `POST` | `/api/compress` | Compress an uploaded file |
| `POST` | `/api/decompress` | Restore a `.huff` file |
| `POST` | `/api/inspect` | Return frequencies and tree information |
| `POST` | `/api/benchmark` | Measure performance and integrity |
| `GET` | `/download/<token>` | Download a generated result |

## 🎬 Suggested demonstration

1. Start the Flask server.
2. Select a text file containing repeated words.
3. Compress it and explain the generated codes.
4. Show original size, compressed size, ratio, savings, and time.
5. Download the `.huff` output.
6. Decompress it and show `integrity_verified = true`.
7. Repeat with a binary or already-compressed file.
8. Explain the difference between theoretical complexity and measured time.

## 🔮 Future enhancements

- LZW implementation and side-by-side algorithm comparison
- Persistent benchmark history and CSV export
- Streaming support for very large files
- Interactive Huffman tree animation
- More detailed benchmark charts and reports

---

<p align="center">
  <strong>Built for learning algorithms through measurable software behavior.</strong><br>
  <sub>Greedy choice • Prefix codes • Correctness • Complexity • Benchmarking</sub>
</p>
