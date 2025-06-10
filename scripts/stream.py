from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
#db
# from langgraph.checkpoint.sqlite import SqliteSaver

model = ChatOllama(
    model="gemma3:4b",
    temperature=0.9, 
    top_p=0.95, 
    num_ctx=2048, 
    repeat_penalty=1.2
)
#Define a new graph
workflow = StateGraph(state_schema=MessagesState)
#define a function that calls model
def call_model(state: MessagesState):
  response = model.invoke(state["messages"])
  return {"messages" : response}

#define a node in the graph
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

#Add memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
config = {"configurable" : {"thread_id" : "thread_1"}}

query = "Tell me a long story"
input_messages = [HumanMessage(content = query)]
# output = app.invoke({"messages": input_messages}, config)
# output["messages"][-1].pretty_print()

for chunk, metadata in app.stream({"messages": input_messages}, config=config}, stream_mode="messages"):
    if isinstance(chunk, AIMessage):
      print(chunk.content, end = "", flush=True)

print("This looks wonderful!")
