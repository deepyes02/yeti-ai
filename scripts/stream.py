# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from pydantic import SecretStr
from langchain_core.runnables import RunnableConfig

model = ChatOpenAI(
    base_url="http://localhost:8080/v1",
    model="mistral-nemo",
    api_key=SecretStr("your_api_key_here"),
    temperature=0.9,
    top_p=0.95,
)
# Define a new graph
workflow = StateGraph(state_schema=MessagesState)


# define a function that calls model
def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": response}


# define a node in the graph
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Add memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
config: RunnableConfig = {"configurable": {"thread_id": "thread_1"}}

query = "Hi, my name is Deepesh, what is your name?"
input_messages = [HumanMessage(content=query)]
# output = app.invoke({"messages": input_messages}, config)
# output["messages"][-1].pretty_prin

for chunk, metadata in app.stream(
    {"messages": input_messages}, config=config, stream_mode="messages"
):
    if isinstance(chunk, AIMessage):
        print(chunk.content, end="", flush=True)

print("This looks wonderful!")
