from langchain_ollama import ChatOllama
import os

def call_the_model(prompt: str) -> str | dict | list:
# initialize with more explicit parameters
  llm = ChatOllama(
      base_url=os.getenv("OLLAMA_BASE_URL","http://host.docker.internal:11434"),
      model="llama3.2:latest", 
      temperature=0.7, 
      top_p=0.95, 
      num_ctx=2048, 
      repeat_penalty=1.2
  )
  response = llm.invoke(prompt)
  return response.content
  