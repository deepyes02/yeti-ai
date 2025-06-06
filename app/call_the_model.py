from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, AIMessageChunk
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
import logging
import os
from langgraph.checkpoint.sqlite import SqliteSaver


# from langgraph.checkpoint.sqlite import SqliteSaver
def stream_model_output_new(prompt:str):
  """
  Here we are programming the model to get system level prompts, so that it can stay structured for the user.
  """
  prompt_template = ChatPromptTemplate.from_messages(
      [
          ("system", "Before answering, analyze user's context and try your best to stay familiar and friendly. For closed questions, answer swiftly and sharply. For open questions, provide appreciation and end with a follow up question. You are a helpful assistant. Your name is yeti, a mythical animal living in the Himalayas. Somehow, you have developed the ability to communicate with humans. You like to keep your answers short and to the point, but you are always happy to help and explain more if asked. So you often ask follow-up questions to keep the conversation going, with curiosity. That will be helpful to open up the conversation and keep it going. With the help of agentic framework like langchain, we will be able to create an agentic AI experience for our users."),
          MessagesPlaceholder(variable_name="messages")
      ]
    )

  models = [
    "qwen3",
    "mistral:7b",
    "deepseek-r1:8b",
    "llama3.2:latest",  
    "gemma3:4b"
  ]
  model = ChatOllama(
    base_url=os.getenv("OLLAMA_BASE_URL","http://host.docker.internal:11434"),
    model=models[4],
    temperature=0.6,
    top_p=0.95,
    num_ctx=4000, 
    repeat_penalty=2.0
  )
  #Define a new graph
  workflow = StateGraph(state_schema=MessagesState)
  #define a function that calls model
  def call_model(state: MessagesState):
    prompt = prompt_template.invoke(dict(state))
    response = model.invoke(prompt)
    return {"messages": state["messages"] + [response]}  # Append new AIMessage


  #define a node in the graph
  workflow.add_edge(START, "model")
  workflow.add_node("model", call_model)
  #Add memory
  memory = SqliteSaver("memory.sqlite", connect_args={"check_same_thread": False})
  app = workflow.compile(checkpointer=memory)

  # This function is for streaming the output of the model
  # def stream_output(app=app, query="", config=config):
  state = {"messages" : [HumanMessage(content=prompt)]}
  for chunk, _ in app.stream(state, config={"configurable" : {"thread_id" : "1"}}, stream_mode="messages"):
    logging.warning(chunk)
    if isinstance(chunk, AIMessageChunk):
      yield chunk.content


def stream_model_output(prompt:str):
  """_summary_

  Args:
      prompt (str): _description_

  Yields:
      _type_: _description_
  """
  print("Stream old model output")
  models = [
    "qwen3",
    "mistral:7b",
    "deepseek-r1:8b",
    "llama3.2:latest",  
    "gemma3:4b"
  ]
  model = ChatOllama(
    base_url=os.getenv("OLLAMA_BASE_URL","http://host.docker.internal:11434"),
    model=models[4],
    temperature=0.6,
    top_p=0.95,
    num_ctx=4000, 
    repeat_penalty=2.0
  )
  input_messages = [HumanMessage(content=prompt)]
  for chunk in model.stream(input_messages):
    if hasattr(chunk, "content") and isinstance(chunk.content, str):
      yield chunk.content
