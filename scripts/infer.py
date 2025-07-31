import os
import sys
import subprocess
from contextlib import redirect_stderr, redirect_stdout

from llama_cpp import Llama

# Redirect stderr (C++ backend logs) and stdout (print output) to log files
log_stderr_path = (
    "/Users/deepesh/Desktop/github-projects/ai-agent/llama_cpp_backend.log"
)

with open(log_stderr_path, "w") as log_file_err, redirect_stderr(log_file_err):
    llm = Llama(
        model_path="/Users/deepesh/llms/mistral-nemo-15.gguf",
        n_ctx=8000,  # Use full context
        n_threads=6,
        n_gpu_layers=-1,
        verbose=True,  # Keep True if you want llama-cpp's Python logs as well
    )

    prompt = "Who was Abraham Lincoln?"

    print("🧠 Response:")
    for chunk in llm(prompt, max_tokens=50, stream=True):
        print(chunk["choices"][0]["text"], end="", flush=True)
