from langchain_core.messages import HumanMessage, AIMessageChunk, SystemMessage
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


def final_answer(state: MessagesState):
    return state


thread_id = 9
projectName = os.environ.get("LANGSMITH_PROJECT")


def agent_router(state):
    messages = state["messages"]
    last = messages[-1]
    if getattr(last, "tool_calls", None) or getattr(last, "tool_call", None):
        return "tools"
    return "final_answer"


##nodes and edges
workflow = StateGraph(state_schema=MessagesState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.add_node("final_answer", final_answer)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", path=agent_router)
workflow.add_edge("tools", "agent")
workflow.add_edge("final_answer", END)
checkpointer_context_manager = PostgresSaver.from_conn_string(conn)
checkpointer = checkpointer_context_manager.__enter__()
checkpointer.setup()
app = workflow.compile(checkpointer=checkpointer)


# We are now using sqlite to remember the context and hence for the agent to remember us by our
# user id
# from langgraph.checkpoint.sqlite import SqliteSaver
def stream_model_output_new(prompt: str):
    """
    Here we are programming the model to get system level prompts, so that it can stay structured for the user. Always write in Markdown format, so it's easier for users to visualize your response.
    """
    # This function is for streaming the output of the model
    state = {
        "messages": [
            SystemMessage(
                content="You are a helpful assistant. When you receive tool results, always summarize them in natural language for the user. Do not show tool call instructions or raw JSON. Only provide the final answer in a user-friendly way. Do not recommend commercial brand names like Accuweather or something else if it seems like user needs more information."
            ),
            HumanMessage(content=prompt),
        ]
    }
    for chunk, _ in app.stream(
        state,
        config={
            "configurable": {"thread_id": thread_id},
            "run_name": f"{projectName}",
            "metadata": {"user_id": thread_id},
        },
        stream_mode="messages",
    ):
        logging.warning(chunk)
        if isinstance(chunk, AIMessageChunk):
            yield chunk.content
