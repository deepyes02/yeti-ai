## Yeti - An agentic artifical intelligence framework 
<img src="yeti-logo.png" alt="Yeti is a mythical mountain creature that several people have reported sightings, looks like human and more intelligent" height="180" width="200">



#### Bring you own model
Using Mistral-Nemo, we are able to mimic compatibility with OPENAI API specification without paying any api key subscription. This enables use to not only work with open source models, but also in future train them, or update them, while seamlessly swapping powerful model into the framework. Imagine lora adapters but for open source models. I think this is useful since most AI services now are behind paywalls, and end user has no option to customize or own the intelligence.

Mistral-Nemo id good for the following reasons: 
1. Capable to carry on meaningful conversation.
2. Ability to call tools and functions for agentic ai application development.
3. Open source and powerful
4. Compatible with OpenAI API, ZERO SHOT, reAct based flow or Langgraph's tool calling framework.
5. Ability to run quantized version in limited GPU environment.

### Tool calling
1. Calling the weather for given city
2. Getting current date and time
3. Finding exchange rate (this is tied to private api so the url  isn't public and can't be used without permission)
4. Searching and summarizing results from the internet.

### Updates 1-September-2025
1. Moved Fast API back into docker, only running inference in the OS for simplicity. Test and minor update.

### Updates 15-August-2025
1. Introduced llama_cpp for inference
2. Moved Fast API to OS, (will restore it inside docker in next update - this was a temporary fix to integrate with llama_cpp inference)

### Updates 11-June-2025
1. Integration with langGraph ecosystem for context awareness and tool calling.
2. Web interface with an exposed chatbot for prompt input.
3. Postgresql database for storing conversation history.

### Still Under developments and extendable features (based on priority)
1. Implementing text-embeddings and vector database to solve context-limit problem and intellectual response based on past conversation.
2. Adding sessions and unique thread ids for classifying conversations based on topic.
2. Adding a search backend for browsing internet for overcoming knowledge cut off.
4. Voice controls & conversation (not urgent).
5. Image analysis. (not so urgent)

### Environment
Llama cpp and fastapi runs from the OS, while the database and frontend loads from docker. As stated in the update, I plan to move fastapi back inside docker in next update. So we will only have our model and inference running in the OS natively, while database, frontend and other management tools are containerized.


### Clone the repo
```sh
git clone https://github.com/deepyes02/yeti-ai # clone this repo
```
### Requirements
1. Install llama_cpp (need to build for specific architecure, see documentation)
2. Install docker Desktop - https://www.docker.com/products/docker-desktop/ 
3. Download Mistral Nemo gguf format quantized model from huggingface.
4. Serve the model from the OS via llama server
   ```bash 
   llama-server -m ~/llms/mistral-nemo-15.gguf --jinja -c 4096
   #context length depends on how much GPU is available
   ```
5. Run uvicorn in the OS, python api for backend and web socket
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 
   ```
6. Run docker in the project root
```bash
docker compose up -d
```
1. And make sure the model name is passed in [load_model.py](./app/utils/load_model.py)

### Note  
To run scripts in [scripts](./scripts/) directory, to enable type checking, and simply testing, it is recommended to install an virutal environment in the project root and also pip install the requirements. Before we move fast api inside docker, this will be important to do. 

```sh
python -m venv env # create env, python 3.11 used in this code, so same is recommended
source ./env/bin/active #activate env
```


### ChatOpenAI wrapper - no need for api key
Mistral-Nemo is compatible with OPENAI api style, hence wrapping the model in Langgraph is similar to what one would do using open ai. The only difference is that there is no need for api key, just pass any string with `SecretStr(<string>)` as ChatOPENAI is originally written with intent to have api_key required.

```py
def load_model():
    model = ChatOpenAI(
        base_url="http://localhost:8080/v1",
        model="mistral-nemo",
        api_key=SecretStr("your_api_key_here"),  #any string is okay for api key, just needs to be there. 
        temperature=0.9,
        top_p=0.95,
    )
    return model
```



The backend server runs on port 8000 and frontend server runs on port 3000 (See docker-compose.yml)
### Visit `localhost:3000` in the browser
<img src="image-1.png" alt="yeti ai chatbot ui" width="440" height="480">

## Some other models I tested
1. Deepseek - okay, but I wasn't able to run non-thinking model as it's quantized model is not available. 
2. Qwen 3 - It comes with a switch to turn on/off the thinking mode. However this is not currently available via ollama. So it is a bit challenging. I have raised an issue on langgraph. 
3. Llama3.2 : Can handle tools but isn't very coherent and keeps making mistake.
4. granite3.3:8b : Promising AI from IBM but still wasn't able to call tools. Need to test this again.

### Reference:
ReAct: Synergizing Reasoning and Acting in Language Models - https://arxiv.org/abs/2210.03629

find me on linkedin: https://linkedin.com/in/deepyes02 for collaboration or opportunities.
