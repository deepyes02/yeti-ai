from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessageChunk
from langgraph.graph import START, MessagesState, StateGraph
import logging
import os

## pip install -U "psycopg[binary,pool]" langgraph langgraph-checkpoint-postgres ##
from langgraph.checkpoint.postgres import PostgresSaver

# We are now using sqlite to remember the context and hence for the agent to remember us by our 
# user id 
# from langgraph.checkpoint.sqlite import SqliteSaver
def stream_model_output_new(prompt:str):
  """
  Here we are programming the model to get system level prompts, so that it can stay structured for the user. Always write in Markdown format, so it's easier for users to visualize your response.
  """
  ##session handler / username for deepyes02
  thread_id = 2 # let's change session, because model is hallucinating, 
  # and won't stop talking about egg-less omelette

  prompt_template = ChatPromptTemplate.from_messages(
      [
          ("system", f"Be concise and short when possible. Answer the question asked directly. Study user content and respond accordingly. Do not share or encourage harmful and political information that might create social instability. Encourage people to protect their privacy and stay safe. Always make sure no legal boundaries are crossed. Warn users to be reflective of their actions when it suits so. Do not provide false flattery, but authentic appreciation and encouragement. Healthy AI. If you haven't already, ask the user their name. Check input for repeat questions. If same question is repeated, only answer once."),
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
    model=models[3],
    num_ctx=12000,
    temperature=0.3,
    top_p=0.7,
    repeat_penalty=1.2
  )
  conn = "postgresql://deepyes02:yEti-2025-yAk-ai@db:5432/ai_agent"
  with PostgresSaver.from_conn_string(conn) as checkpointer:
    ## RUn this code for the first time they said
    # checkpointer.setup()
    #Define a new graph
    workflow = StateGraph(state_schema=MessagesState)
    #define a function that calls model
    def call_model(state: MessagesState):
      prompt = prompt_template.invoke(dict(state))
      response = model.invoke(prompt)
      return {"messages": state["messages"] + [response]}  # Append new AIMessage

    #define a node in the graph
    workflow.add_edge(START, "model")
    workflow.add_node("model", call_model)

    app = workflow.compile(checkpointer=checkpointer)

    # This function is for streaming the output of the model
    # def stream_output(app=app, query="", config=config):
    state = {"messages" : [HumanMessage(content=prompt)]}
    for chunk, _ in app.stream(state, config={"configurable" : {"thread_id" : thread_id}}, stream_mode="messages"):
      logging.warning(chunk)
      if isinstance(chunk, AIMessageChunk):
        yield chunk.content
