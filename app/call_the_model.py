from langchain_ollama import ChatOllama
import os

## a simple model call function for example purposes
def call_the_model(prompt: str) -> str | dict | list:
# initialize with more explicit parameters
  models = [
    "qwen3",
    "mistral:7b",
    "deepseek-r1:8b",
    "llama3.2:latest",
  ]
  llm = ChatOllama(
      base_url=os.getenv("OLLAMA_BASE_URL","http://host.docker.internal:11434"),
      model=models[0],
      temperature=0.6,
      top_p=0.95,
      num_ctx=2048, 
      repeat_penalty=2.0
  )
  response = llm.invoke(prompt)
  return response.content
