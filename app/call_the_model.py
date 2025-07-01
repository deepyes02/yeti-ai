from langchain_core.messages import HumanMessage, AIMessageChunk, SystemMessage
from langgraph.graph import START, MessagesState, StateGraph, END
from langgraph.prebuilt import create_react_agent, ToolNode
import logging, os
from app.utils.system_prompt import system_prompt
from app.utils.load_model import load_model
from dotenv import load_dotenv

from app.utils.tool_calling.get_exchange_rates import get_exchange_rates
from app.utils.tool_calling.get_weather import get_weather
from app.utils.tool_calling.web_search_summary import make_search_tool
from app.utils.tool_calling.current_datetime import make_datetime_tool
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.runnables import RunnableConfig

load_dotenv()

conn = os.environ.get("POSTGRESQL_URL", "")
if not conn:
    raise ValueError("POSTGRESQL_URL environment variable is not set.")

model = load_model()
search_tool = make_search_tool(model)
datetime_tool = make_datetime_tool()

##describe agent node and tool node
agent_node = create_react_agent(
    model, [get_weather, get_exchange_rates, search_tool, datetime_tool]
)
tool_node = ToolNode([get_weather, get_exchange_rates, search_tool, datetime_tool])


def agent_router(state):
    messages = state["messages"]
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
workflow.add_edge("agent", END)
checkpointer_context_manager = PostgresSaver.from_conn_string(conn)
checkpointer = checkpointer_context_manager.__enter__()
checkpointer.setup()

app = workflow.compile(checkpointer=checkpointer)

# We are now using sqlite to remember the context and hence for the agent to remember us by our
# user id
# from langgraph.checkpoint.sqlite import SqliteSaver


def stream_model_output_new(prompt: str, thread_id=9999):
    """
    Here we are programming the model to get system level prompts, so that it can stay structured for the user. Always write in Markdown format, so it's easier for users to visualize your response.
    """
    config: RunnableConfig = {
        "configurable": {"thread_id": thread_id},
        "metadata": {"user_id": thread_id},
    }
    prev_state = app.get_state(config=config)
    # prev_state is likely a tuple, so access by index 0 for the state dict
    prev_state_message = (
        prev_state[0]["messages"]
        if prev_state
        and isinstance(prev_state[0], dict)
        and "messages" in prev_state[0]
        else []
    )
    # logging.warning(f"Previous state: {prev_state_message}")
    if not prev_state or not prev_state_message:
        logging.warning("No previous state found, initializing new state.")
        state = {
            "messages": [
                SystemMessage(content=system_prompt()),
                HumanMessage(content=prompt),
            ]
        }
    else:
        logging.warning("Previous state found, appending to existing messages.")
        prev_state[0]["messages"].append(HumanMessage(content=prompt))
        state = prev_state[0]

    for chunk, _ in app.stream(
        state,
        config=config,
        stream_mode="messages",
    ):
        # logging.warning(chunk)
        if isinstance(chunk, AIMessageChunk):
            yield chunk.content
