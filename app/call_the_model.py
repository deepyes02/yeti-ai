from langchain_ollama import ChatOllama
import os

## a simple model call function for example purposes
def call_the_model(prompt: str) -> str | dict | list:
# initialize with more explicit parameters
  llm = ChatOllama(
      base_url=os.getenv("OLLAMA_BASE_URL","http://host.docker.internal:11434"),
      model="llama3.2:latest",
      temperature=0.6,
      top_p=0.95,
      num_ctx=2048, 
      repeat_penalty=2.0
  )
  response = llm.invoke(prompt)
  return response.content
