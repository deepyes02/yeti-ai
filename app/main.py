from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.call_the_model import stream_model_output_new
import asyncio
import threading
import logging
import json
from datetime import datetime

### Enable Langsmith by uncommenting below options
# from app.utils.load_environment import load_environment_variables
# load_environment_variables()

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Yeti Backend starting up...")
    logger.info("📡 WebSocket endpoint available at: ws://localhost:8000/ws")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Yeti Backend shutting down...")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = id(websocket)
    # Visual separator for new connection
    print("\n" + "=" * 60)
    logger.info(f"🔌  NEW CONNECTION REQUEST | Client #{client_id}")
    print("=" * 60 + "\n")
    
    await websocket.accept()
    logger.info(f"✅  CONNECTED | Client #{client_id} | Channel OPEN")
    
    message_count = 0
    
    while True:
        try:
            prompt = await websocket.receive_text()
            message_count += 1
            
            # Message received decoration
            print("\n" + "-" * 40)
            logger.info(f"📨  MESSAGE #{message_count} RECEIVED | Client #{client_id}")
            logger.info(f"📝  PROMPT:  '{prompt[:100]}'{'...' if len(prompt) > 100 else ''}")
            print("-" * 40 + "\n")
            
            try:
                chunk_count = 0
                start_time = datetime.now()
                
                # Natively await the async generator for minimum latency
                async for obj in stream_model_output_new(prompt):
                    chunk_count += 1
                    await websocket.send_text(json.dumps(obj))
                    
                    # Log first chunk and every 10th chunk for progress tracking
                    if chunk_count == 1:
                        elapsed = (datetime.now() - start_time).total_seconds()
                        logger.info(f"⚡  FIRST TOKEN | Time: {elapsed:.2f}s | Client #{client_id}")
                    elif chunk_count % 10 == 0:
                        logger.debug(f"📦  STREAMING | {chunk_count} chunks sent...")
                
                elapsed_total = (datetime.now() - start_time).total_seconds()
                logger.info(f"✅  RESPONSE COMPLETE | {chunk_count} chunks | Total: {elapsed_total:.2f}s")
                print("\n" + "." * 60 + "\n")
                
            except Exception as e:
                logger.error(f"❌  STREAM ERROR | Client #{client_id} | {e}", exc_info=True)
                error_message = {"type": "chunk", "data": f"Sorry, I encountered an error: {e}"}
                await websocket.send_text(json.dumps(error_message))
                
        except WebSocketDisconnect:
            logger.info(f"🔌  DISCONNECTED | Client #{client_id} | Total Msgs: {message_count}")
            print("=" * 60 + "\n")
            break
        except Exception as e:
            logger.error(f"❌  WEBSOCKET ERROR | Client #{client_id} | {e}", exc_info=True)
            print("=" * 60 + "\n")
            break


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
