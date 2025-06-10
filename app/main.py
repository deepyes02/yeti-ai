from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.call_the_model import stream_model_output_new
import asyncio
import threading
import logging

### Enable Langsmith by uncommenting below options
# from app.utils.load_environment import load_environment_variables
# load_environment_variables()
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
        response = "<think> Okay, the user has been repeatedly saying \"hi\" and \"hello,\" which seems like they're testing how I respond or just trying to get a reaction. They might be bored with the conversation flow or looking for something different. I need to keep things friendly but also encourage them to share more about what they want to talk about. Since we've had previous conversations, maybe they're not sure if I remember those interactions. I should acknowledge their greetings and invite them to ask questions or discuss any topic they're interested in. It's important to stay positive and open-ended so the conversation can move forward naturally without getting stuck in a loop. Also, considering the user mentioned working on an AI model earlier, maybe they have technical questions or want to explore more about how I function. But since their current messages are just greetings, it's better to keep the response light and engaging. </think> It seems like we've started fresh again! What’s on your mind today? Would you like to chat about something specific—or is there an old topic (like chess, exchange rates, or even that eggless omelette mystery) you’d like to revisit? I’m here to help whenever you’re ready! 😊"

        words = response.split(" ")
        for word in response:
          await websocket.send_text(word)
          await asyncio.sleep(0.01)
