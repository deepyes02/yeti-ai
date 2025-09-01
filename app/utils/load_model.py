from contextlib import redirect_stderr
from langchain_community.chat_models import ChatLlamaCpp
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from dotenv import load_dotenv
import os

load_dotenv()


def load_model():
    model = ChatOpenAI(
        base_url=os.environ.get("INFERENCE_API_URL"),
        model="mistral-nemo",
        api_key=SecretStr("some-fake-strings"),
        temperature=0.9,
        top_p=0.95,
    )
    return model
