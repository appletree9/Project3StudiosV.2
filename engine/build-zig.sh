#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
# Alternative compiler used for the bundled binary: pip install ziglang
python -m ziglang c++ sculpt.cpp -target wasm32-wasi -std=c++20 -O3 -msimd128 -fno-exceptions -fno-rtti -mexec-model=reactor \
 -Wl,--export=positions -Wl,--export=normals -Wl,--export=indices -Wl,--export=capacity -Wl,--export=setup \
 -Wl,--export=checkpoint -Wl,--export=undo -Wl,--export=recalc -Wl,--export=dab -Wl,--export=pick \
 -Wl,--export=hitx -Wl,--export=hity -Wl,--export=hitz -Wl,--initial-memory=134217728 -Wl,--max-memory=134217728 -Wl,--export=drag_begin -Wl,--export=drag_update -o sculpt.wasm
