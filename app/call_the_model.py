from langchain_core.messages import HumanMessage, AIMessageChunk
from langgraph.graph import START, MessagesState, StateGraph, END
from langgraph.prebuilt import create_react_agent, ToolNode
import logging, os
from app.utils.system_prompt import system_prompt
from app.utils.load_model import load_model
from dotenv import load_dotenv

from app.utils.tool_calling.get_exchange_rates import get_exchange_rates
from app.utils.tool_calling.get_weather import get_weather
from langgraph.checkpoint.postgres import PostgresSaver

load_dotenv()

conn = os.environ.get("POSTGRESQL_URL", "")
if not conn:
    raise ValueError("POSTGRESQL_URL environment variable is not set.")

prompt_template = system_prompt()
model = load_model()

##describe agent node and tool node
agent_node = create_react_agent(model, [get_weather, get_exchange_rates])
tool_node = ToolNode([get_weather, get_exchange_rates])

def call_model(state: MessagesState):
  prompt = prompt_template.invoke(dict(state))
  response = model.invoke(prompt)
  return {"messages": state["messages"] + [response]}

thread_id = 5
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
