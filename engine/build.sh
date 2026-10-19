#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
em++ sculpt.cpp -std=c++20 -O3 -flto -msimd128 --no-entry -s STANDALONE_WASM=1 -s INITIAL_MEMORY=134217728 -s ALLOW_MEMORY_GROWTH=0 -Wl,--export-memory -o sculpt.wasm
