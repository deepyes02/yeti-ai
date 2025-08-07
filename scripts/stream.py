# from langchain_community.chat_models import ChatOpenAI
import os
import uuid
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from pydantic import SecretStr
from langchain_core.runnables import RunnableConfig

# Load environment variables from .env file
load_dotenv()

# It's better to load sensitive info and configs from environment variables
# to avoid hardcoding them. I see you have a .env.sample, so I'll assume
# you're using a .env file for configuration.
model = ChatOpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:8080/v1"),
    model=os.getenv("OLLAMA_MODEL", "mistral-nemo"),
    api_key=SecretStr(os.getenv("OPENAI_API_KEY", "not-needed")),
    temperature=0.9,
    top_p=0.95,
)
# Define a new graph
workflow = StateGraph(MessagesState)


# define a function that calls model
def call_model(state: MessagesState) -> dict[str, list[BaseMessage]]:
    """Invokes the model with the current state and returns the new message."""
    response = model.invoke(state["messages"])
    # We return a list with the new AIMessage to be appended to the state.
    # Your original code returned the message object directly, which would cause an error.
    return {"messages": [response]}


# define a node in the graph
workflow.add_node("model", call_model)
workflow.add_edge(START, "model")

# Add memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


def main():
    # Using a unique thread_id for each conversation.
    config: RunnableConfig = {
        "configurable": {"thread_id": f"thread_{uuid.uuid4().hex[:8]}"}
    }
    query = "Hi, my name is Deepesh, what is your name?"
    input_messages = [HumanMessage(content=query)]

    print(f"--- Running query: '{query}' ---")
    print("\n--- AI Response ---")
    final_chunk = None
    # Your original streaming loop had an invalid `stream_mode` and was trying to unpack two values.
    # The `app.stream()` method with a non-streaming model call will yield the final state after all steps.
    for chunk in app.stream({"messages": input_messages}, config=config):
        final_chunk = chunk

    if final_chunk:
        last_message = final_chunk["messages"][-1]
        if isinstance(last_message, AIMessage):
            # This will print the full response at the end, not token-by-token.
            # For true streaming, the model call inside the node needs to change to `model.stream()`.
            print(last_message.content)

    print("\n\nThis looks wonderful!")


if __name__ == "__main__":
    main()
