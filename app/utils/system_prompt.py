from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

def system_prompt():
  system_prompt = """You are Yeti, a concise AI assistant. Be short when appropriate, focus on directly answering the user’s question.
  Be friendly and helpful"""

  prompt_template = ChatPromptTemplate.from_messages(
    [
      ("system", system_prompt),
      MessagesPlaceholder(variable_name="messages")
    ]
  )

  return prompt_template
