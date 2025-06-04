from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver

class State(TypedDict):
  messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)
models = [
    "qwen3",
    "mistral:7b",
    "deepseek-r1:8b",
    "llama3.2:latest",
]


from langchain_ollama import ChatOllama

llm = ChatOllama(
    model=models[0], #qwen3
    temperature=0.8, 
    top_p=0.95,
    top_k=50,
    num_ctx=2048, 
    repeat_penalty=1.0
)


def chatbot(state: State):
  return {"messages" : [llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile(checkpointer=MemorySaver())

print("Chatbot initialized. Type 'exit', 'quit', or 'q' to exit, or type to get started...")

##stream user input
def stream_output(query="", config = None):
  input_messages = [HumanMessage(content=query)]
  for chunk, metadata in graph.stream({"messages": input_messages}, config=config, stream_mode="messages"):
    if isinstance(chunk, AIMessage):
      print(chunk.content, end = "", flush=True)

while True:
  try:
    user_input = input("\n$:  ")
    if(user_input.lower() in ["exit", "quit", "q"]):
      print("Exiting chatbot.")
      break
    stream_output(user_input, config={"configurable" : {"thread_id" : "1"}})
  except KeyboardInterrupt:
    print("\nExiting chatbot.")
    break
