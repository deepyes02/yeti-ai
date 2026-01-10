#!/bin/bash
mkdir -p slots
# llama-server -m /Users/deepesh/Desktop/bin/llms/mistral-nemo-15.gguf --jinja -c 32768 -ngl 99 -fa -cb --cache-type-k q4_0 --cache-type-v q4_0 -t 6 -tb 6 -b 2048 -ub 2048 --mlock --slot-save-path ./slots

llama-server -m $(dirname "$0")/models/shisa-v2-mistral-nemo-12b.Q4_K_M.gguf \
  --jinja \
  -c 32000 \
  -ngl 99 \
  -fa \
  -cb \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  -t 8 \
  -tb 8 \
  -b 512 \
  -ub 512 \
  --mlock \
  --slot-save-path ./slots

