from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.call_the_model import stream_model_output_new
import asyncio
import threading
import logging

app = FastAPI()

# app.add_middleware(
#   CORSMiddleware,
#   allow_origins=["http://localhost:3000"],
#   allow_credentials=True,
#   allow_methods=["*"],
#   allow_headers=["*"]
# )

import threading
from queue import Queue

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    logging.warning("Inside web socket")
    await websocket.accept()
    while True:
        try:
            prompt = await websocket.receive_text()
        except WebSocketDisconnect:
            break

        q = Queue()

        def produce():
            for chunk in stream_model_output_new(prompt):
                q.put(chunk)
            q.put(None)  # Sentinel value

        threading.Thread(target=produce, daemon=True).start()

        while True:
            chunk = await asyncio.get_event_loop().run_in_executor(None, q.get)
            logging.warning(chunk)
            if chunk is None:
                break
            await websocket.send_text(chunk)

@app.websocket("/ws-decoy")
async def mock_stream(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            await websocket.receive_text()
        except WebSocketDisconnect:
            break

        # Simulated response with <think> and normal content
        response = "<think>I see the user asked about websocket chunking. Let's pretend I'm an AI thinking through the steps. I'll need to simulate streaming behavior.</think> Sure! I'm now streaming this response as if it were real output from a language model. Let me know if you need another example!"

        words = response.split(" ")
        for word in words:
          await websocket.send_text(word + " ")
          await asyncio.sleep(0.05)