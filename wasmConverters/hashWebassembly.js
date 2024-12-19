let hashMD5Module, hashSHA256Module, hashCRC32Module;

// Load MD5 WebAssembly module
async function loadMD5() {
    hashMD5Module = await import('./hashMD5.js');
}

// Load SHA256 WebAssembly module
async function loadSHA256() {
    hashSHA256Module = await import('./hashSHA256.js');
}

// Load CRC32 WebAssembly module
async function loadCRC32() {
    hashCRC32Module = await import('./hashCRC32.js');
}

// Wait for all modules to load
async function init() {
    await loadMD5();
    await loadSHA256();
    await loadCRC32();
}

// Generate hashes when button is clicked
function generateHashes() {
    const inputText = document.getElementById('inputText').value;

    const md5Hash = hashMD5Module._hashMD5(inputText);
    const sha256Hash = hashSHA256Module._hashSHA256(inputText);
    const CRC32Hash = hashCRC32Module._hashCRC32(inputText);

    document.getElementById('md5Result').textContent = `MD5: ${md5Hash}`;
    document.getElementById('sha256Result').textContent = `SHA256: ${sha256Hash}`;
    document.getElementById('CRC32Result').textContent = `CRC32: ${CRC32Hash}`;
}

// Initialize modules
init();