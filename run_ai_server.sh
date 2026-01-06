#!/bin/bash
llama-server -m /Users/deepesh/Desktop/bin/llms/mistral-nemo-15.gguf --jinja -c 32768 -ngl 99 -fa -cb --cache-type-k q4_0 --cache-type-v q4_0


