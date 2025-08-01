from contextlib import redirect_stderr
from langchain_community.chat_models import ChatLlamaCpp


def load_model():
    log_path = "/Users/deepesh/Desktop/github-projects/ai-agent/app/logs/llama_cpp.log"

    with open(log_path, "w") as log_file, redirect_stderr(log_file):
        model = ChatLlamaCpp(
            model_path="/Users/deepesh/llms/mistral-nemo-15.gguf",
            temperature=0.9,
            top_p=0.95,
            n_ctx=12000,
            repeat_penalty=1.2,
            n_gpu_layers=-1,
            verbose=False,
        )
        return model
