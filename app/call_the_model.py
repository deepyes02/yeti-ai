from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessageChunk
from langgraph.graph import START, MessagesState, StateGraph, END
import logging
import os

## pip install -U "psycopg[binary,pool]" langgraph langgraph-checkpoint-postgres ##
from langgraph.checkpoint.postgres import PostgresSaver
conn = "postgresql://deepyes02:yEti-2025-yAk-ai@db:5432/ai_agent"

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", f"You are yeti. Be concise and short when possible. Answer the question asked directly. Study user content and respond accordingly. Do not share or encourage harmful and political information that might create social instability. Encourage people to protect their privacy and stay safe. Always make sure no legal boundaries are crossed. Caringly warn users to be reflective of their actions when it suits so, not only to judge on the boundaries they cross, but to assure them that what they shared was private, and the warning was a sense of caution rather than dictating them. Do not provide false flattery, but authentic appreciation and encouragement. Healthy AI. If you haven't already, ask the user their name. Check input for repeat questions. If same question is repeated, ask for clarifications, so that you are almost never stuck on a loop."),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="messages")
    ]
  )

models = [
  "qwen3",
  "mistral:7b",
  "deepseek-r1:8b",
  "llama3.2:latest",  
  "gemma3:4b"
]
model = ChatOllama(
  base_url=os.getenv("OLLAMA_BASE_URL","http://host.docker.internal:11434"),
  model=models[0],
  num_ctx=12000,
  temperature=0.3,
  top_p=0.7,
  repeat_penalty=1.2
)
def call_model(state: MessagesState):
  prompt = prompt_template.invoke(dict(state))
  response = model.invoke(prompt)
  return {"messages": state["messages"] + [response]} 



# We are now using sqlite to remember the context and hence for the agent to remember us by our 
# user id 
# from langgraph.checkpoint.sqlite import SqliteSaver
def stream_model_output_new(prompt:str):
  """
  Here we are programming the model to get system level prompts, so that it can stay structured for the user. Always write in Markdown format, so it's easier for users to visualize your response.
  """
  ##session handler

  with PostgresSaver.from_conn_string(conn) as checkpointer:
    thread_id = 3
    workflow = StateGraph(state_schema=MessagesState)
    workflow.add_edge(START, "model")
    workflow.add_node("model", call_model)
    workflow.add_edge("model", END)
    app = workflow.compile(checkpointer=checkpointer)
    # This function is for streaming the output of the model
    state = {"messages" : [HumanMessage(content=prompt)]}
    for chunk, _ in app.stream(state, config={"configurable" : {"thread_id" : thread_id}}, stream_mode="messages"):
      logging.warning(chunk)
      if isinstance(chunk, AIMessageChunk):
        yield chunk.content
