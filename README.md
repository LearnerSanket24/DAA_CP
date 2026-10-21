# Smart File Compression Workbench

A Flask web application for demonstrating byte-level Huffman coding as a Design and Analysis of Algorithms project.

For the complete explanation to present to a teacher, see
[PROJECT_FLOW.md](PROJECT_FLOW.md). It includes the system flow, implementation
details, DAA complexity analysis, demonstration procedure, and likely viva questions.

## Features

- Huffman coding implemented from scratch with a min-heap and binary tree.
- Lossless compression and decompression for arbitrary binary files.
- Fixed, self-describing `.huff` format with a 256-entry frequency table.
- Compression ratio, complete output size, space savings, and timing metrics.
- Prefix-code table and algorithm explanation in the web interface.
- Benchmark endpoint and pytest coverage for empty, single-symbol, text, and binary inputs.

## Project flow

1. Upload a file through the Flask web interface.
2. Read the file as raw bytes and count frequencies for values `0..255`.
3. Build a Huffman tree using a min-priority queue.
4. Generate prefix-free binary codes by traversing the tree.
5. Encode and pack the bits into bytes.
6. Store the original size, frequency table, and payload in a `.huff` stream.
7. Calculate compression statistics and display the result.
8. Rebuild the tree during decompression and verify exact byte restoration.

## Run on Windows

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in a browser.

Run the tests with:

```powershell
pytest -q
```

## Complexity

For `n` input bytes and `k` distinct symbols, frequency counting and encoding take `O(n)`. Building the Huffman tree takes `O(k log k)` with a binary min-heap, and the auxiliary algorithmic structures use `O(k)` space. The implementation uses a byte alphabet, so `k <= 256`.
