from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.call_the_model import call_the_model, stream_model_output

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:3000"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
)

@app.websocket("/ws")
async def websocket_endpoint(websocket : WebSocket):
  await websocket.accept()
  while True:
    prompt = await websocket.receive_text()
    async for chunk in stream_model_output(prompt):
      if not isinstance(chunk, str):
        chunk = str(chunk)
      await websocket.send_text(chunk)

@app.get("/")
def home():
  return {"response": "Hello world"}

@app.get("/user/{user_id}")
def get_user(user_id: int):
  return {"response", user_id}

@app.get("/chat")
async def get_chat():
  return {"response": call_the_model("नमस्ते। आप कैसे हैं?")}

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    prompt = body.get("prompt")
    return {"response": call_the_model(prompt)}