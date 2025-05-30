## DECENTRALIZED INTELLIGENCE ##
The idea is to integrate blockchain but that is far fetched.

## Why ##
I want to have a personalized AI model and to do things for me, like go on a website and fetch information. I want several of the information I share to be private.

### Developments:
1. Data persistence via threads.
2. Data streaming for real time response.
3. Backend server

### Requirements:
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

#### Start Docker 
```bash
docker compose up -d
## or docker compose up --build for first time
```

#### Make a POST Request with prompt
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

