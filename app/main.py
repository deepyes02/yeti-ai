from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.call_the_model import call_the_model, stream_model_output
import logging
import asyncio
import threading
from queue import Queue
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:3000"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
)

import threading
from queue import Queue

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            prompt = await websocket.receive_text()
        except WebSocketDisconnect:
            break

        q = Queue()

        def produce():
            for chunk in stream_model_output(prompt):
                q.put(chunk)
            q.put(None)  # Sentinel value

        threading.Thread(target=produce, daemon=True).start()

        while True:
            chunk = await asyncio.get_event_loop().run_in_executor(None, q.get)
            if chunk is None:
                break
            await websocket.send_text(chunk)

@app.get("/")
def home():
  logger.info("Hello from logger")
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