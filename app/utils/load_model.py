from contextlib import redirect_stderr
from langchain_community.chat_models import ChatLlamaCpp
from langchain_openai import ChatOpenAI
from pydantic import SecretStr


def load_model():
    model = ChatOpenAI(
        base_url="http://localhost:8080/v1",
        model="mistral-nemo",
        api_key=SecretStr("your_api_key_here"),
        temperature=0.9,
        top_p=0.95,
    )
    return model
