from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessageChunk
from langgraph.graph import START, MessagesState, StateGraph, END
import logging
import os
from app.utils.system_prompt import system_prompt
from dotenv import load_dotenv
load_dotenv()

## pip install -U "psycopg[binary,pool]" langgraph langgraph-checkpoint-postgres ##
from langgraph.checkpoint.postgres import PostgresSaver
conn = "postgresql://deepyes02:yEti-2025-yAk-ai@db:5432/ai_agent"

prompt_template = system_prompt()

models = [
  "qwen3",
  "mistral:7b",
  "deepseek-r1:8b",
  "llama3.2:latest",  
  "gemma3:4b"
]
model = ChatOllama(
  base_url=os.getenv("OLLAMA_BASE_URL","http://host.docker.internal:11434"),
  model=models[1],
  num_ctx=12000,
  temperature=0.3,
  top_p=0.7,
  repeat_penalty=1.2
)
def call_model(state: MessagesState):
  prompt = prompt_template.invoke(dict(state))
  response = model.invoke(prompt)
  return {"messages": state["messages"] + [response]} 


thread_id = 4
projectName = os.environ.get("LANGSMITH_PROJECT")
workflow = StateGraph(state_schema=MessagesState)
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)
workflow.add_edge("model", END)
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
