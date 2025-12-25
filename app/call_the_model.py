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
from app.utils.tool_calling.current_datetime import get_current_datetime
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_core.runnables import RunnableConfig

load_dotenv()

conn = os.environ.get("POSTGRESQL_URL", "")
if not conn:
    raise ValueError("POSTGRESQL_URL environment variable is not set.")

model = load_model()
search_tool = make_search_tool(model)

tools = [get_weather, get_exchange_rates, search_tool, get_current_datetime]

# We'll initialize the checkpointer inside the async generator or as a global async object
# For simplicity with FastAPI lifespan or local usage, we can create it here but it needs an async loop to setup
async def get_app():
    checkpointer = AsyncPostgresSaver.from_conn_string(conn)
    # Note: version 0.2+ of langgraph-checkpoint-postgres uses aio
    # We'll use a simplified approach for the app compilation
    return create_react_agent(model, tools, checkpointer=checkpointer)

# We are now using sqlite to remember the context and hence for the agent to remember us by our
# user id
# from langgraph.checkpoint.sqlite import SqliteSaver


async def stream_model_output_new(prompt: str, thread_id=1):
    """
    Yields structured dictionary objects for the frontend asynchronously.
    """
    config: RunnableConfig = {
        "configurable": {"thread_id": thread_id},
        "metadata": {"user_id": thread_id},
    }
    
    async with AsyncPostgresSaver.from_conn_string(conn) as checkpointer:
        await checkpointer.setup()
        app = create_react_agent(model, tools, checkpointer=checkpointer)
        
        prev_state = await app.aget_state(config=config)
        prev_state_message = (
            prev_state.values["messages"]
            if prev_state and prev_state.values and "messages" in prev_state.values
            else []
        )

        if not prev_state or not prev_state_message:
            state = {
                "messages": [
                    SystemMessage(content=system_prompt()),
                    HumanMessage(content=prompt),
                ]
            }
        else:
            last_msg = prev_state_message[-1] if prev_state_message else None
            if isinstance(last_msg, HumanMessage):
                prev_state.values["messages"].append(AIMessageChunk(content="Okay."))
            prev_state.values["messages"].append(HumanMessage(content=prompt))
            state = prev_state.values

        # Use stream_mode=["messages", "updates"] to catch both content and graph transitions
        async for stream_type, chunk in app.astream(
            state,
            config=config,
            stream_mode=["messages", "updates"],
        ):
            if stream_type == "messages":
                msg, metadata = chunk
                if isinstance(msg, AIMessageChunk) and msg.content:
                    yield {"type": "chunk", "data": msg.content}
            
            elif stream_type == "updates":
                if "agent" in chunk:
                    yield {"type": "signal", "status": "thinking"}
                elif "tools" in chunk:
                    yield {"type": "signal", "status": "searching"}
