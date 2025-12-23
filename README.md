# Yeti – An Agentic Artificial Intelligence Framework

<img src="yeti-logo.png" alt="Yeti logo – a mythical intelligent mountain creature" height="180" width="200">

Yeti is a framework for building **agentic AI applications** with support for open-source large language models, tool calling, and modular extensions.

---

## Key Features

### Bring Your Own Model
Yeti leverages **`Mistral-Nemo`**, providing compatibility with the `OpenAI API` specification without requiring an API subscription. This approach enables:

- Seamless use of open-source models.  
- Future capability to train, fine-tune, or update models.  
- Flexible model swapping (similar to `LoRA` adapters but for open-source models).  
- Greater control and ownership over intelligence, avoiding proprietary paywalls.

**Why `Mistral-Nemo`?**
1. Handles meaningful conversations effectively.
2. Supports tool and function calling for agentic AI development.
3. Fully open-source and powerful.
4. Compatible with `OpenAI API`, zero-shot, `ReAct`-based flows, and `LangGraph`’s tool-calling framework.
5. Can run quantized versions in limited GPU environments.

---

### Tool Calling
Out-of-the-box support includes:
1. Fetching weather for a given city.
2. Getting the current date and time.
3. Fetching exchange rates (via private API).
4. Searching and summarizing results from the internet.

## Roadmap (Planned Features)
1. Text embeddings and vector database for overcoming context limits.  
2. Session and thread IDs for topic-based conversation classification.  
3. Integrated search backend for browsing the internet.  
4. Voice controls and conversational interaction (low priority).  
5. Image analysis (low priority).  

---

## Architecture

- **Host OS**: Runs `llama_cpp` inference 
- **Docker**: Runs database, frontend and `FastAPI` backend.  
---

## Getting Started

### Clone the Repository
```sh
git clone https://github.com/deepyes02/yeti-ai
```

### Requirements
1. Install `llama_cpp` (compile for your specific architecture; see documentation).  
2. Install [`Docker Desktop`](https://www.docker.com/products/docker-desktop/).  
3. Download the **`Mistral-Nemo`** quantized GGUF model from Hugging Face.  
4. Serve the model locally:
   ```bash
   llama-server -m ~/llms/mistral-nemo-15.gguf --jinja -c 4096
   # Adjust context length based on available GPU
   ```
5. Run the backend (`FastAPI` + `WebSocket`):
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
6. Start `Docker` containers in the project root:
   ```bash
   docker compose up -d
   ```
7. Ensure the model name is correctly configured in [`load_model.py`](./app/utils/load_model.py).

---

## Development Notes

For testing, type checking, and script execution in [`scripts/`](./scripts/), it is recommended to set up a virtual environment in the project root:

```sh
python -m venv env   # Python 3.11 recommended
source ./env/bin/activate
pip install -r requirements.txt
```

---

## ChatOpenAI Wrapper (No API Key Required)

`Mistral-Nemo` is **`OpenAI API`-compatible**. Wrapping it in `LangGraph` works just like using `OpenAI`, except no real API key is required:

```python
def load_model():
    model = ChatOpenAI(
        base_url="http://localhost:8080/v1",
        model="mistral-nemo",
        api_key=SecretStr("any_string_here"),  # any placeholder string works
        temperature=0.9,
        top_p=0.95,
    )
    return model
```

---

## Running the Application

- **Backend server**: Port `8000`  
- **Frontend server**: Port `3000` (see `docker-compose.yml`)  

Visit: [http://localhost:3000](http://localhost:3000)  

<img src="image-1.png" alt="Yeti AI chatbot UI" width="440" height="480">

---

## Tested Models

1. **`DeepSeek`** – Works, but limited by lack of quantized non-thinking model.  
2. **`Qwen 3`** – Has a “thinking mode” toggle, but not yet supported via `Ollama`. (Issue raised with `LangGraph`.)  
3. **`Llama 3.2`** – Handles tools but often produces incoherent results.  
4. **`Granite 3.3 (8B)`** – Promising IBM model, but tool-calling not yet functional (needs more testing).  

---

## References

- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)

---
