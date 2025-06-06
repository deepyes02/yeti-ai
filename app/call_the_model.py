from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
import os
import logging
##today we will learn how to program an AI
def stream_model_output(prompt:str):
  prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "Before answering, analyze user's context and try your best to stay familiar and friendly. For closed questions, answer swiftly and sharply. For open questions, provide appreciation and end with a follow up question. You are a helpful assistant. Your name is yeti, a mythical animal living in the Himalayas. Somehow, you have developed the ability to communicate with humans. You like to keep your answers short and to the point, but you are always happy to help and explain more if asked. So you often ask follow-up questions to keep the conversation going, with curiosity. That will be helpful to open up the conversation and keep it going. With the help of agentic framework like langchain, we will be able to create an agentic AI experience for our users."),
        MessagesPlaceholder(variable_name="messages")
    ]
  )
  models = [
    "gemma3:4b",
    "mistral:7b",
    "deepseek-r1:8b",
    "llama2-uncensored:latest",
    "llama3.2:latest",
    "qwen2.5:14b",
    "starcoder2:3b"
  ]
  model = ChatOllama(
    base_url=os.getenv("OLLAMA_BASE_URL","http://host.docker.internal:11434"),
    model=models[4],
    temperature=0.6,
    top_p=0.95,
    num_ctx=4000, 
    repeat_penalty=2.0
  )
  logging.warning("🔧 Hello from call the model")
  #Define a new graph
  workflow = StateGraph(state_schema=MessagesState)
  #define a function that calls model
  def call_model(state: MessagesState):
    print("Curreent state:", state)
    prompt = prompt_template.invoke(dict(state))
    response = model.invoke(prompt)
    return {"messages" : response}
  
  #define a node in the graph
  workflow.add_edge(START, "model")
  workflow.add_node("model", call_model)
  #Add memory
  memory = MemorySaver()
  app = workflow.compile(checkpointer=memory)
  # Two different threads representing two different conversations

  # Allocating state and remembering the threads will enable the model to have multiple conversation
  config = {"configurable" : {"thread_id" : "1"}}
  config_2 = {"configurable" : {"thread_id" : "2"}}

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
