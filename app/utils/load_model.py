from contextlib import redirect_stderr
from langchain_community.chat_models import ChatLlamaCpp
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logger = logging.getLogger(__name__)

def load_model():
    inference_url = os.environ.get("INFERENCE_API_URL", "http://host.docker.internal:8080/v1")
    
    print("\n" + "╔" + "═" * 50 + "╗")
    logger.info(f"║ 🤖  LOADING MODEL")
    logger.info(f"║ 🔗  URL: {inference_url}")
    print("╚" + "═" * 50 + "╝\n")
    
    model = ChatOpenAI(
        base_url=inference_url,
        model="mistral-nemo",
        api_key=SecretStr("some-fake-strings"),
        temperature=0.9,
        top_p=0.95,
    )
    
    logger.info("✅  MODEL LOADED & READY")
    return model
