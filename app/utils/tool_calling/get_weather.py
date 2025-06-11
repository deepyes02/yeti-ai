from langchain.agents import tool
@tool
def get_weather(city:str) -> str:
  """Get the weather for a given city"""
  return f"The weather in {city} is unknown at this moment. Please check later"