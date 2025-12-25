# Yeti – Full-stack AI Agent

The Shipton Footprints (1951): Perhaps the most famous "evidence" ever found. British mountaineer Eric Shipton took photos of massive, humanoid tracks in the snow near Mount Everest. Each print was about 13 inches long and very wide. These photos sparked a "Yeti-mania" that lasted decades. 

**`Mistral-Nemo`** 
Mistral Nemo was good at reasoning and calling functions with less confusion.
---

### Tool Calling
Currently the agent is able to:  
1. Fetch weather for a given city.  
2. Get the current date and time.  
3. Fetching exchange rates
4. Search and summarize results from the internet.  

```python
from langchain.agents import tool  

@tool
def get_product_price(labubu: int) -> str:
    """Get the price of a product."""
    return get_price(labubu) 
```
```txt
Prompt example: 
Hey, what's the price of labulu? 
### Process: 
- calls the appropriate function get_product_price(labubu), captures the response and send it to the user automaticaly: 
### Response:
==> Ah yes, the price of labubu is 20$.
```


## Needs more work here:
1. Text embeddings and vector database for overcoming context limits.  
2. Managing session and thread IDs / user logins.  
3. Better search libaray for browsing the internet.
4. Voice controls (low priority).
5. Image analysis (low priority).  
---

## Architecture
- **Host OS**: Runs `llama_cpp` inference (download llama_cpp, an AI model and serve from your OS).
- **Docker**: Database, frontend and backend microservices in separate containers.
---

### Clone the Repository

### Requirements
1. Install [`llama_cpp`](https://github.com/ggml-org/llama.cpp)
2. Install [`Docker Desktop`](https://www.docker.com/products/docker-desktop/). 
3. Download the **`Mistral-Nemo`** quantized GGUF model from Hugging Face.

4. Serve the model on your OS.
   ```bash
   llama-server -m ~/llms/mistral-nemo-15.gguf --jinja -c 4096
   # Adjust context length based on available GPU
   ```

5. Start frontend, backend and microservices on the container
**Make sure the llama server is running before starting the containers**
From the root directory of the project, run:
   ```bash
   docker compose up -d
   ```
   Fires up Next JS frontend, FASTAPI backend and database service.
6. Ensure the model name is correctly configured in [`load_model.py`](./app/utils/load_model.py).

---
---

## Accessing the Application

- **Backend server**: Port `8000`  
- **Frontend server**: Port `3000` (see `docker-compose.yml`)  

Visit: [http://localhost:3000](http://localhost:3000)  

<img src="assets/image.png" alt="Yeti AI chatbot UI" width="800" height="800">

---

## Development Notes

There are various notebooks and scripts for local testing in [`scripts/`](./scripts/), I set up a virtual environment in the project root and install the requirements.txt locally so it helps to execute those tests locally. It is not necessary to do this.

```sh
python -m venv env   # Python 3.11 recommended
source ./env/bin/activate
pip install -r requirements.txt
```
---

## ChatOpenAI Wrapper
Yeti uses **`OpenAI API`-compatible** models. So, wrapping it in `LangGraph` works just like using `OpenAI`, with random api_key

```python
def load_model():
    model = ChatOpenAI(
        base_url="http://localhost:8080/v1",
        model="mistral-nemo",
        api_key=SecretStr("just_some_string_maybe_the_name_of_your_ex_works_here"),  # no need for OPEN API key
        temperature=0.9,
        top_p=0.95,
    )
    return model
```

## User Interface  
Built on React and NEXT JS, the frontend utilizes websocket to consume and stream responses from the server. The app can hence be fully customized and extended.

## Attach and Debug

I normally attach to the running docker containers to debug backend logs and errors while developing, it is helpful.

## Tested Models
I tested these other models during the project, they work but Mistral Nemo was the best.
1. **`DeepSeek`**
2. **`Qwen 3`**`LangGraph`  
3. **`Llama 3.2`**
4. **`Granite 3.3 (8B)`** 

## Reference
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
