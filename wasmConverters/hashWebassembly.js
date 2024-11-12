let hashMD5Module, hashSHA256Module, hashWhirlpoolModule;

// Load MD5 WebAssembly module
async function loadMD5() {
    hashMD5Module = await import('./hashMD5.js');
}

// Load SHA256 WebAssembly module
async function loadSHA256() {
    hashSHA256Module = await import('./hashSHA256.js');
}

// Load Whirlpool WebAssembly module
async function loadWhirlpool() {
    hashWhirlpoolModule = await import('./hashWhirlpool.js');
}

// Wait for all modules to load
async function init() {
    await loadMD5();
    await loadSHA256();
    await loadWhirlpool();
}

// Generate hashes when button is clicked
function generateHashes() {
    const inputText = document.getElementById('inputText').value;

    const md5Hash = hashMD5Module._hashMD5(inputText);
    const sha256Hash = hashSHA256Module._hashSHA256(inputText);
    const whirlpoolHash = hashWhirlpoolModule._hashWhirlpool(inputText);

    document.getElementById('md5Result').textContent = `MD5: ${md5Hash}`;
    document.getElementById('sha256Result').textContent = `SHA256: ${sha256Hash}`;
    document.getElementById('whirlpoolResult').textContent = `Whirlpool: ${whirlpoolHash}`;
}

// Initialize modules
init();