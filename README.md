## Yeti - An agentic artifical intelligence framework 
<img src="yeti-logo.png" alt="Yeti is a mythical mountain creature that several people have reported sightings, looks like human and more intelligent" height="180" width="200">

Using models with tool-calling capability, this ai framework is able to converse and run api functions. Very good for private use of AI without spilling personal data.

### Updates 11-June-2025
1. Integration with langGraph ecosystem for context awareness and tool calling.
2. Web interface with an exposed chatbot for prompt input.
3. Postgresql database for storing conversation history.

### Still Under developments and extendable features
1. Adding sessions and unique thread ids for classifying conversations based on topic.
1. Implementing text-embeddings and vector database to solve context-limit problem and intellectual response based on past conversation.
2. Adding a search backend for browsing internet for overcoming knowledge cut off.
4. Voice controls & conversation (not urgent).
5. Image analysis. (not so urgent)

### Challenges
- Not having a strong PC with GPU capabilities to run models faster, or run bigger models.

### Requirements
1. Install Ollama - https://ollama.com/download
2. Download llama3.2 model (able to call tools): `ollama pull llama3.2:latest` or `ollama run llama3.2:latest` . The model will take some time to download.

```bash
$ ollama ls
NAME               ID              SIZE      MODIFIED
qwen3:latest       500a1f067a9f    5.2 GB    6 days ago #thinking / non-thinking 
mistral:latest     f974a74358d6    4.1 GB    6 days ago #non-thinking / not great tool support
gemma3:4b          a2af6cc3eb7f    3.3 GB    2 weeks ago #doesn't support tool_calling
deepseek-r1:8b     28f8fd6cdc67    4.9 GB    4 months ago #thiking
llama3.2:latest    a80c4f17acd5    2.0 GB    7 months ago #not thinking / tool support 
```
3. And make sure the model name is passed in [call_the_model.py](./app/call_the_model.py)
```py
models = ["qwen3","mistral:7b","deepseek-r1:8b","llama3.2:latest","gemma3:4b"]
model = ChatOllama(
  base_url=os.getenv("OLLAMA_BASE_URL","http://host.docker.internal:11434"),
  model=models[2], #We are running deepseek here.
  num_ctx=12000,
  temperature=0.3,
  top_p=0.7,
  repeat_penalty=1.2
)
```

### Clone this repository and install docker
In the project root, run
```bash
git clone https://github.com/deepyes02/yeti-ai # clone this repo
## First time
docker compose up --build
## Later
docker compose up # or
docker compose up -d #detached mode

docker container ls
$ docker container ls
CONTAINER ID   IMAGE                           COMMAND                  CREATED         STATUS         PORTS                           NAMES
2e6f3c2794d2   dpage/pgadmin4                  "/entrypoint.sh"         6 seconds ago   Up 5 seconds   443/tcp, 0.0.0.0:5050->80/tcp   ai-agent-pgadmin-1
bd5261cc8934   ai-agent-frontend               "docker-entrypoint.s…"   6 seconds ago   Up 5 seconds   0.0.0.0:3000->3000/tcp          web
928c748485bf   postgres:15                     "docker-entrypoint.s…"   6 seconds ago   Up 5 seconds   0.0.0.0:5432->5432/tcp          ai-agent-db-1
8a20cd91f862   ai-agent-backend                "uvicorn app.main:ap…"   6 seconds ago   Up 5 seconds   0.0.0.0:8000->8000/tcp          api_backend
1392623f254b   moby/buildkit:buildx-stable-1   "buildkitd"              13 hours ago    Up 13 hours                                    buildx_buildkit_loving_jemison0

```

The backend server runs on port 8000 and frontend server runs on port 3000 (See docker-compose.yml)
### Visit `localhost:3000` in the browser
<img src="image-1.png" alt="yeti ai chatbot ui" width="440" height="480">


### Tool calling
See [scripts/tool_calling.py](./scripts/tool_calling.py)  



### Local installation  for running scripts (Optional)
Useful for locally testing files in script folders.
```bash
#project root folder
python -m venv env
pip install --upgrade pip
pip install -r requirements.txt
source env/bin/activate ##active virtual environment
deactivate ##deactivate virtual environment
```

#### Model Comparision
1. Deepseek - struggled to know prominent figure like "Laxmi Prasad Devkota" of Nepal, meaning its knowledge isn't wider, required for common sense. Also the think mode is really a lot of tokens not relevant to user.
2. Mistral : Good, but not able to call tools.
3. Llama3.2 : Is smart and can handle errors. Can call tools. The quantized version isn't very coherent. 
4. granite3.3:8b : Promising but still wasn't able to call tools.

ReAct: Synergizing Reasoning and Acting in Language Models - https://arxiv.org/abs/2210.03629

