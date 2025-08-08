#!/bin/bash
llama-server -m ~/llms/mistral-nemo-15.gguf --jinja -c 4096 & \
uvicorn app.main:app --host 0.0.0.0 --port 8000 