import os
from langchain_ollama import ChatOllama

def load_model():
  models = ["qwen3", "mistral:7b","deepseek-r1:8b","llama3.2:latest","gemma3:4b"]
  model = ChatOllama(
    base_url=os.getenv("OLLAMA_BASE_URL","http://host.docker.internal:11434"),
    model=models[3],
    num_ctx=12000,
    temperature=0.3,
    top_p=0.7,
    repeat_penalty=1.2
  )
  return model