from langchain_ollama import ChatOllama

llm = ChatOllama(model="qwen2.5:14b", temperature=0.7, top_p=0.95, num_ctx=2048, repeat_penalty=1.2)

prompt = "Please tell me a lighthearted joke."
response = llm.invoke(prompt)

print(response.content)
