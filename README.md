## OPEN SOURCE INTELLIGENCE ##
Using open source AI models with tool calling capabilities, it is possible to write an intelligent program that can do agentic functions. In this project, I am trying to create a personalized experience with the use of artifical intelligence driven by langchain and other agentic ai frameworks.

![Yeti is a mythical mountain creature that several people have reported sightings, looks like human and more intelligent](yeti.png)
### Capabilities
1. Streaming chat output to the web server with websocket
2. Saving user data in sqlite
3. Displaying 


## Why ##
Customize and bring open source models to the world. Enable private use of AI with secure information.

### Developments:
1. Data persistence via threads.
2. Data streaming for real time response.
3. Backend ai server (langchain, fastapi)
4. Web Server (Next JS)

### Dependencies:
1. Ollama and local models (Running in OS)
2. Docker (for server)

### Installation 
For easy type hinting or running notebooks in local computer, add an env and install requirements
```bash
#project root folder
python -m venv env
pip install --upgrade pip
pip install -r requirements.txt
```
![Screenshot](image-1.png)

#### Start Docker 
```bash
docker compose up -d
## or docker compose up --build for first time
```

### Frontend
Hooked up our frontend with Next JS so that we can get the best of React.

#### API
API can be developed like this via fast api
##### Add body with prompt on the POST Request
```txt
POST http://localhost:8000/chat
```

```json
{
  "prompt": "Tell me a joke"
}
```
#### The response is also JSON
```json
{
  "response": "Here's one:\n\nWhat do you call a fake noodle?\n\nAn impasta.\n\n(I hope that made your day!) Do want to hear another? I have plenty of them! :) )"
}
```

#### Tool calling
With Llama, mistral and qwen, tool calling is possible. See ```scripts/tool_calling.py``` for more details. It is a test tool that returns static result, and the model is able to handle it.

### Dependencies
1. ## pip install -U "psycopg[binary,pool]" langgraph langgraph-checkpoint-postgres ##