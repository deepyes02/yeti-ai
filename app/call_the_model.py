from langchain_core.messages import HumanMessage, AIMessageChunk
from langgraph.graph import START, MessagesState, StateGraph, END
from langgraph.prebuilt import create_react_agent, ToolNode
from langchain.agents import tool
import requests, json, logging, os
from app.utils.system_prompt import system_prompt
from app.utils.load_model import load_model
from dotenv import load_dotenv
load_dotenv()

@tool
def get_weather(city:str) -> str:
  """Get the weather for a given city"""
  return f"The weather in {city} is unknown at this moment. Please check later"
@tool
def get_exchange_rates(from_currency: str, to_currency: str):
    """Get exchange rate for a given currency pair."""
    EXCHANGE_JP = os.getenv("EXCHANGE_JP")
    if not EXCHANGE_JP:
        raise ValueError("EXCHANGE_JP environment variable is not set.")
    response = requests.get(EXCHANGE_JP)
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}")
    response_json = response.json()
    rates = json.loads(response_json["Rates"])
    currency = rates["ALL_ALL_ALL"]["Currency"]
    print(currency)

    exchange_rate_data = []
    for value in currency:
        data = currency[value]
        exchange_rate_data.append(
            {
                "sender_unit": float(1),
                "sender_currency": data["From"],
                "receiver_unit": float(data["SellingRate"]),
                "receiver_currency": data["To"],
            }
        )
    for rate in exchange_rate_data:
      if rate["sender_currency"] == from_currency and rate["receiver_currency"] == to_currency:
        return f"%s" % rate["receiver_unit"]
    return f"Sorry we don't have exchange rate for {from_currency} to {to_currency}."

## pip install -U "psycopg[binary,pool]" langgraph langgraph-checkpoint-postgres ##
from langgraph.checkpoint.postgres import PostgresSaver
conn = "postgresql://deepyes02:yEti-2025-yAk-ai@db:5432/ai_agent"

prompt_template = system_prompt()
model = load_model()

##describe agent node and tool node
agent_node = create_react_agent(model, [get_weather, get_exchange_rates])
tool_node = ToolNode([get_weather, get_exchange_rates])

def call_model(state: MessagesState):
  prompt = prompt_template.invoke(dict(state))
  response = model.invoke(prompt)
  return {"messages": state["messages"] + [response]} 

thread_id = 2
projectName = os.environ.get("LANGSMITH_PROJECT")
def agent_router(state):
    messages = state['messages']
    last = messages[-1]
    
    if getattr(last, "tool_calls", None) or getattr(last, "tool_call", None):
      return "tools"
    return END

##nodes and edges 
workflow = StateGraph(state_schema=MessagesState)

workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.add_edge(START, "agent")

workflow.add_conditional_edges("agent", path=agent_router)
workflow.add_edge("tools", "agent")
workflow.add_node("call_model", call_model)
workflow.add_edge("call_model", END)

# We are now using sqlite to remember the context and hence for the agent to remember us by our 
# user id 
# from langgraph.checkpoint.sqlite import SqliteSaver
def stream_model_output_new(prompt:str):
  """
  Here we are programming the model to get system level prompts, so that it can stay structured for the user. Always write in Markdown format, so it's easier for users to visualize your response.
  """
  ##session handler
  with PostgresSaver.from_conn_string(conn) as checkpointer:
    checkpointer.setup()
    app = workflow.compile(checkpointer=checkpointer)
    # This function is for streaming the output of the model
    state = {"messages" : [HumanMessage(content=prompt)]}
    for chunk, _ in app.stream(state,
    config={
      "configurable" : {"thread_id" : thread_id},
      "run_name" : f"{projectName}",
      "metadata" : {"user_id" : thread_id}
        },
    stream_mode="messages"):
      logging.warning(chunk)
      if isinstance(chunk, AIMessageChunk):
        yield chunk.content
