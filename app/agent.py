from app.langgraph_setup import app as agent_app
from langchain_core.messages import HumanMessage

def run_agent(prompt: str):
    input_msg = {"messages": [HumanMessage(content=prompt)]}
    response = agent_app.invoke(input_msg)
    return response["messages"][-1].content