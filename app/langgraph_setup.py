from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver

model = ChatOllama(
    model="llama3",
    base_url="http://ollama:11434",
    temperature=0.7,
    top_p=0.95
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder("messages")
])
chain = prompt | model

def agent_node(state: MessagesState):
    response = chain.invoke(state)
    return {"messages": state["messages"] + [response]}

graph = StateGraph(MessagesState)
graph.add_node("agent", agent_node)
graph.set_entry_point(START)
graph.add_edge(START, "agent")
graph.add_edge("agent", END)
graph.set_finish_point(END)

memory = MemorySaver()
app = graph.compile(checkpointer=memory)