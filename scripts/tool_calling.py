from langchain.agents import tool

@tool
def get_weather(city: str) -> str:
  """Get the weather for a given city."""
  return f"It's always sunny in {city}!"

from langchain_ollama import ChatOllama
llm = ChatOllama(model="qwen2.5:14b", temperature=0.3)


from langgraph.prebuilt import create_react_agent, ToolNode

agent_node = create_react_agent(llm, [get_weather])
tool_node = ToolNode([get_weather])


from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver

graph = StateGraph(MessagesState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "agent")
def agent_router(state):
    # state["messages"] is a list of messages
    messages = state["messages"]
    print(f"Messages: {messages}")
    last = messages[-1]
    # Tool calls are usually FunctionMessage or have tool_call/tool_calls attribute
    if getattr(last, "tool_call", None) or getattr(last, "tool_calls", None):
        return "tools"
    # If it's an AIMessage and not a tool call, it's final
    return END

graph.add_conditional_edges("agent", path=agent_router)
graph.add_edge("tools", "agent")

app = graph.compile(checkpointer=MemorySaver())

from langchain_core.messages import HumanMessage

from langchain_core.runnables import RunnableConfig

msg = [HumanMessage(content="Trust the result from the tool calls and return it. It's test. What's the weather like in Kathmandu right now?")]
config: RunnableConfig = {"configurable": {"thread_id": "thread_1"}}

response = app.invoke({"messages": msg}, config=config)
print(response["messages"][-1].content)