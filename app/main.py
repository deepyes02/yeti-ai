from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.call_the_model import call_the_model, stream_model_output
import logging
logger = logging.getLogger(__name__)



app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:3000"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print('WebSocket endpoint hit', flush=True)
    await websocket.accept()
    try:
        while True:
            try:
                prompt = await websocket.receive_text()
            except WebSocketDisconnect:
                print("Client disconnected", flush=True)
                break
            except Exception as e:
                print(f"Error receiving data: {e}", flush=True)
                continue

            full_response = ""
            for chunk in stream_model_output(prompt):
                if not isinstance(chunk, str):
                    chunk = str(chunk)

                # Deduplicate: skip if chunk is already inside response
                if chunk in full_response:
                    continue

                print(f"[send] {chunk}", flush=True)
                await websocket.send_text(chunk)
                full_response += chunk
    except Exception as e:
        print(f"Fatal error: {e}", flush=True)
        await websocket.close()
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