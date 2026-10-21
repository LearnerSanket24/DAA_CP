const input = document.querySelector("#file-input");
const zone = document.querySelector("#drop-zone");
const browse = document.querySelector("#browse-button");
const compressButton = document.querySelector("#compress-button");
const benchmarkButton = document.querySelector("#benchmark-button");
const status = document.querySelector("#status");
let selectedFile = null;

function setFile(file) {
  selectedFile = file;
  document.querySelector("#file-title").textContent = file.name;
  document.querySelector("#file-meta").textContent = `${formatBytes(file.size)} selected`;
  compressButton.disabled = false;
  benchmarkButton.disabled = false;
  status.textContent = "Ready to process.";
  status.className = "status";
}
function formatBytes(size) {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(2)} MB`;
}
function setStatus(message, kind = "") {
  status.textContent = message;
  status.className = `status ${kind}`;
}
async function processFile(endpoint) {
  if (!selectedFile) return;
  setStatus("Processing with the custom Huffman engine…");
  compressButton.disabled = true;
  benchmarkButton.disabled = true;
  const body = new FormData();
  body.append("file", selectedFile);
  try {
    const response = await fetch(endpoint, { method: "POST", body });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "The operation failed.");
    if (endpoint.endsWith("benchmark")) {
      showBenchmark(data);
    } else {
      showResult(data);
    }
    setStatus("Operation completed successfully.", "success");
  } catch (error) {
    setStatus(error.message, "error");
  } finally {
    compressButton.disabled = false;
    benchmarkButton.disabled = false;
  }
}
function showResult(data) {
  document.querySelector("#results").classList.remove("hidden");
  document.querySelector("#original-size").textContent = formatBytes(data.original_size);
  document.querySelector("#compressed-size").textContent = formatBytes(data.compressed_size);
  document.querySelector("#ratio").textContent = `${data.compression_ratio.toFixed(2)}×`;
  document.querySelector("#savings").textContent = `${data.space_savings.toFixed(2)}%`;
  document.querySelector("#elapsed").textContent = `${data.elapsed_ms.toFixed(2)} ms`;
  document.querySelector("#integrity").textContent = data.integrity_verified ? "Verified" : "Failed";
  document.querySelector("#symbol-count").textContent = `${data.distinct_symbols} distinct symbols`;
  document.querySelector("#download-link").href = data.download_url;
  document.querySelector("#codes").innerHTML = data.codes.map(item =>
    `<tr><td>${item.symbol}</td><td>${item.frequency.toLocaleString()}</td><td>${item.code}</td></tr>`).join("");
  const tree = data.tree;
  document.querySelector("#tree-summary").textContent = tree
    ? `Root frequency: ${tree.frequency.toLocaleString()} bytes. Every leaf path is a prefix-free code.`
    : "The input is empty, so its Huffman tree has no nodes.";
  document.querySelector("#results").scrollIntoView({ behavior: "smooth", block: "start" });
}
function showBenchmark(data) {
  showResult({
    ...data,
    elapsed_ms: data.compression_ms + data.decompression_ms,
    codes: [],
    distinct_symbols: 0,
    tree: null,
    download_url: "#",
  });
  document.querySelector("#download-link").classList.add("hidden");
  document.querySelector("#elapsed").textContent = `C ${data.compression_ms.toFixed(2)} / D ${data.decompression_ms.toFixed(2)} ms`;
  document.querySelector("#codes").innerHTML = "<tr><td colspan='3'>Benchmark mode: code table omitted.</td></tr>";
}
browse.addEventListener("click", () => input.click());
zone.addEventListener("click", (event) => { if (event.target !== browse) input.click(); });
input.addEventListener("change", () => { if (input.files[0]) setFile(input.files[0]); });
["dragenter", "dragover"].forEach(name => zone.addEventListener(name, event => {
  event.preventDefault(); zone.classList.add("over");
}));
["dragleave", "drop"].forEach(name => zone.addEventListener(name, event => {
  event.preventDefault(); zone.classList.remove("over");
}));
zone.addEventListener("drop", event => { if (event.dataTransfer.files[0]) setFile(event.dataTransfer.files[0]); });
compressButton.addEventListener("click", () => processFile("/api/compress"));
benchmarkButton.addEventListener("click", () => processFile("/api/benchmark"));
