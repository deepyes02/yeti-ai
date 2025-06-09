<img src="yeti.png" alt="Yeti is a mythical mountain creature that several people have reported sightings, looks like human and more intelligent" height="180" width="300">

## Yeti AI  
### An agentic artifical intelligence framework 
Yeti ai is an open-sourced, artifical intelligence framework built with langchain ecosystem. The architecture is separated by concerns, so expansion to the project to native app is possible. All services (frontend, backend, database) runs on docker containers. For the LLMs, ollama and some freely available models are using, specifically the ones with tool-calling activity.

### Requirements
1. [Install Ollama]("https://ollama.com/")
2. Pull some models `ollama run modelName`
  For example
  ```bash
$ ollama ls
NAME               ID              SIZE      MODIFIED
qwen3:latest       500a1f067a9f    5.2 GB    6 days ago
mistral:latest     f974a74358d6    4.1 GB    6 days ago
llava:latest       8dd30f6b0cb1    4.7 GB    6 days ago
llava:7b           8dd30f6b0cb1    4.7 GB    7 days ago
gemma3:4b          a2af6cc3eb7f    3.3 GB    2 weeks ago
mistral:7b         f974a74358d6    4.1 GB    2 months ago
deepseek-r1:8b     28f8fd6cdc67    4.9 GB    4 months ago
llama3.2:latest    a80c4f17acd5    2.0 GB    7 months ago
starcoder2:3b      f67ae0f64584    1.7 GB    10 months ago
```
3. And make sure the model name is passed in [call_the_model.py](./app/call_the_model.py)
```py
models = [
  "qwen3",
  "mistral:7b",
  "deepseek-r1:8b",
  "llama3.2:latest",  
  "gemma3:4b"
]
model = ChatOllama(
  base_url=os.getenv("OLLAMA_BASE_URL","http://host.docker.internal:11434"),
  model=models[2], #We are running deepseek here.
  num_ctx=12000,
  temperature=0.3,
  top_p=0.7,
  repeat_penalty=1.2
)
```
3. Make sure docker is available and running

### Get started 
In the project root, run
```bash
docker compose up # or
docker compose up -d
## For building first time, you can also
docker compose up --build
```

The backend server runs on port 8000 and frontend server runs on port 3000 (See docker-compose.yml)
### Visit `localhost:3000` in the browser
![Screenshot](image-1.png)


### Tool Calling with reAsoning and AcTing (reAct) prompting
Tool calling is important to hook our model with a python function. See [scripts/tool_calling.py](./scripts/tool_calling.py)


### Developments:
1. A functional chatbot that takes user inputs and streams them back
2. Decoupled backend (fastapi), database(postgresql) and frontend(NextJS).

## Working on
1. Authenticating user and connecting with Session IDs.
2. Tool calling integration in the browser. See [tool_calling.ipynb](./scripts/tool_calling.ipynb) or [tool_calling.py](./scripts/tool_calling.py)

## Tool calling 
With Llama, mistral and qwen, tool calling is possible. Some models like gemma are not able to call tools, so please pick one of above models. See ```scripts/tool_calling.py``` for more details. It is a test tool that returns static result, and the model is able to handle it.

### Local installation  for running scripts (Optional)
For easy type hinting or running notebooks in local computer, or executing scripts inside the scrips folder for testing, it is easier to also install the python package locally and also help in code completions and syntax highlighting.

```bash
#project root folder
python -m venv env
pip install --upgrade pip
pip install -r requirements.txt
source env/bin/activate
```
