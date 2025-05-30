from langchain_ollama import ChatOllama
# from memory import user_preference, user_saved_memory

# initialize with more explicit parameters
llm = ChatOllama(
    model="llama3.2:latest",
    temperature=0.6,
    top_p=0.95,
    num_ctx=2048,
    repeat_penalty=2.0,
)

prompt = "Hi how are you?"
response = llm.invoke(prompt)
print(response.content)

print(f"\nend of code")
