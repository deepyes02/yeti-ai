from langchain_ollama import ChatOllama
import random
from memory import user_preference, user_saved_memory
from utilities.load_environment import load_environment_variables

# This function connects langsmith, so make sure to only call it when needed
# load_environment_variables()
# initialize with more explicit parameters
llm = ChatOllama(
    model="mistral:7b", 
    temperature=0.7, 
    top_p=0.95, 
    num_ctx=2048, 
    repeat_penalty=1.2,
    timeout=120
)
user_preference = user_preference()
user_memory = user_saved_memory()

pre_prompt = f"Here are my preferences: {user_preference}. And here are the list of things you know about me: {user_memory}"

prompt = "What are my preferences that I have listed out in our conversation? Also, can you also list out the things that you know about me, based on the information I have shared so far ?"
response = llm.invoke(pre_prompt + ' '+ prompt)

print(response.content)
print(f"\nend of code")
