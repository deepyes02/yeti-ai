from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
import os

def stream_model_output(prompt:str):
  models = [
    "qwen3",
    "mistral:7b",
    "deepseek-r1:8b",
    "llama3.2:latest",
  ]
  model = ChatOllama(
    base_url=os.getenv("OLLAMA_BASE_URL","http://host.docker.internal:11434"),
    model=models[1],
    temperature=0.6,
    top_p=0.95,
    num_ctx=4000, 
    repeat_penalty=2.0
  )
  input_messages = [HumanMessage(content=prompt)]
  for chunk in model.stream(input_messages):
    if hasattr(chunk, "content") and isinstance(chunk.content, str):
      yield chunk.content

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
      model=models[3],
      temperature=0.6,
      top_p=0.95,
      num_ctx=2048, 
      repeat_penalty=2.0
  )
  response = llm.invoke(prompt)
  return response.content
