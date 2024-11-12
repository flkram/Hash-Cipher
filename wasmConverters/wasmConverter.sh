#!/bin/bash

# Compile hashMD5.cpp to WebAssembly
emcc hashMD5.cpp -o hashMD5.js -s WASM=1 -s EXPORTED_FUNCTIONS='["_hashMD5"]' -s "EXTRA_EXPORTED_RUNTIME_METHODS=['cwrap']"

# Compile hashSHA256.cpp to WebAssembly
emcc hashSHA256.cpp -o hashSHA256.js -s WASM=1 -s EXPORTED_FUNCTIONS='["_hashSHA256"]' -s "EXTRA_EXPORTED_RUNTIME_METHODS=['cwrap']"

# Compile hashWhirlpool.cpp to WebAssembly
emcc hashWhirlpool.cpp -o hashWhirlpool.js -s WASM=1 -s EXPORTED_FUNCTIONS='["_hashWhirlpool"]' -s "EXTRA_EXPORTED_RUNTIME_METHODS=['cwrap']"
