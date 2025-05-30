from langchain_ollama import ChatOllama
# from memory import user_preference, user_saved_memory



# initialize with more explicit parameters
llm = ChatOllama(
    model="llama3.2:latest", 
    temperature=0.7, 
    top_p=0.95, 
    num_ctx=2048, 
    repeat_penalty=1.2,
)


prompt = "Hi how re you?"
response = llm.invoke(prompt)
print(response.content)

print(f"\nend of code")
