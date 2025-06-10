from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
# from memory import user_preference, user_saved_memory
# from utilities.load_environment import load_environment_variables

# This function connects langsmith, so make sure to only call it when needed
# load_environment_variables()
# initialize with more explicit parameters
llm = ChatOllama(
    model="qwen3", 
    temperature=0.3, 
    top_p=0.95, 
    num_ctx=2048, 
    repeat_penalty=1.2,
)
# user_preference = user_preference()
# user_memory = user_saved_memory()

# pre_prompt = f"Here are my preferences: {user_preference}. And here are the list of things you know about me: {user_memory}"

# prompt = "What are my preferences that I have listed out in our conversation? Also, can you also list out the things that you know about me, based on the information I have shared so far ?"

# response = llm.invoke([HumanMessage(content = pre_prompt + ' '+ prompt)])

response = llm.invoke(
    [
        HumanMessage(content="Hi! I'm Bob"),
        AIMessage(content="Hello Bob! How can I assist you today?"),
        HumanMessage(content="What's my name?"),
    ]
)

print(response.content)
print(f"\nend of code")
