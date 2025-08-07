#!/bin/bash
llama-server -m ~/llms/mistral-nemo-15.gguf --jinja -c 65536 & \
uvicorn app.main:app --host 0.0.0.0 --port 8000 