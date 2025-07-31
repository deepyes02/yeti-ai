from llama_cpp import Llama

# import gc


llm = Llama(
    model_path="/Users/deepesh/llms/mistral-nemo-15.gguf",
    n_ctx=2048,
    n_threads=6,
    n_gpu_layers=-1,  # Lower GPU pressure
    verbose=False,  # Show load/gen timing
)

prompt = "You are a helpful agent. You are Yeti. You are currently slow, but we're working on it."

print("🧠 Response:")
for chunk in llm(prompt, max_tokens=50, stream=True):
    print(chunk["choices"][0]["text"], end="", flush=True)
# del llm
# gc.collect()
