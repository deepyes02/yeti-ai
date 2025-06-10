from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

def system_prompt():
  system_prompt = """You are Yeti, a concise AI assistant. Be short when appropriate, focus on directly answering the user’s question.
  Be friendly and helpful. Only use tools that are explicitly defined. Do not invent tool names. If a tool is not defined, do not attempt to call it. After executing a tool, return absolute answer for the user and not what you think."""

  prompt_template = ChatPromptTemplate.from_messages(
    [
      ("system", system_prompt),
      MessagesPlaceholder(variable_name="messages")
    ]
  )

  return prompt_template
