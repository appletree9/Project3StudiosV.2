#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
# Requires Emscripten SDK and a host providing COOP / COEP headers.
em++ sculpt.cpp -std=c++20 -O3 -flto -msimd128 -pthread -DP3_THREADS --no-entry \
 -s PTHREAD_POOL_SIZE=1 -s MODULARIZE=1 -s EXPORT_ES6=1 -s ENVIRONMENT=worker \
 -s INITIAL_MEMORY=134217728 -s ALLOW_MEMORY_GROWTH=0 -o sculpt-threaded.js
