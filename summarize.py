from langchain_ollama import ChatOllama
import random
# from memory import user_preference, user_saved_memory

with open('long_text.txt', 'r') as f:
  long_text = f.read()


# initialize with more explicit parameters
llm = ChatOllama(
    model="deepseek-r1:8b", 
    temperature=0.7, 
    top_p=0.95, 
    num_ctx=2048, 
    repeat_penalty=1.2,
    timeout=120
)

# user_preference = user_preference()
# user_memory = user_saved_memory()

pre_prompt = f"{long_text}"

prompt = "Summarize the following text into minimum possible concise sentences. Focus on summarizing the core of the whole description. Remove fillers or irrelevant details. Maintain a neutral tone without exaggeration. Try to be as minimial and precise as possible."
response = llm.invoke(pre_prompt + ' ' + prompt)
print(response.content)

print(f"\nend of code")
