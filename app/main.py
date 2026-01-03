from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.call_the_model import stream_model_output_new
from app.utils.tool_calling.current_datetime import get_current_datetime
from app.utils.tool_calling.get_weather import get_weather
from app.utils.tool_calling.get_exchange_rates import get_exchange_rates
from app.utils.tool_calling.web_search_summary import search_web
import asyncio
import threading
import logging
import json
import re
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

# --- Middleware ---
class IPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "Unknown"
        # Log IP for every request (or store in request state for later use)
        # request.state.client_ip = client_ip 
        # logger.info(f"🌍 Request from IP: {client_ip} | Path: {request.url.path}")
        response = await call_next(request)
        return response

app.add_middleware(IPMiddleware)

# --- Direct Tool Routes ---

@app.get("/api/time")
async def get_time_route(request: Request):
    client_ip = request.client.host if request.client else "Unknown"
    logger.info(f"🕒 Time request from IP: {client_ip}")
    return {"result": get_current_datetime.invoke({})}

@app.get("/api/weather")
async def get_weather_route(request: Request, city: str = "Chiyoda, Tokyo"):
    client_ip = request.client.host if request.client else "Unknown"
    logger.info(f"🌤️ Weather request for {city} from IP: {client_ip}")
    # get_weather expects a string argument named 'city' but invoked as tool
    result = get_weather.invoke({"city": city})
    return {"result": result}

@app.get("/api/rate")
async def get_rate_route(request: Request, from_curr: str = "JPY", to_curr: str = "INR"):
    client_ip = request.client.host if request.client else "Unknown"
    logger.info(f"💱 Rate request {from_curr}->{to_curr} from IP: {client_ip}")
    result = get_exchange_rates.invoke({"from_currency": from_curr, "to_currency": to_curr})
    # Tool returns dict or string, let's ensure we pass it back cleanly
    return {"result": result}

@app.get("/api/search")
async def get_search_route(request: Request, q: str = "Digital Wallet Corporation"):
    client_ip = request.client.host if request.client else "Unknown"
    logger.info(f"🔍 Search request for '{q}' from IP: {client_ip}")
    result = search_web(q)
    return {"result": result}

@app.get("/api/lore/shipton")
async def get_shipton_lore(request: Request):
    client_ip = request.client.host if request.client else "Unknown"
    logger.info(f"👣 Lore request (Shipton) from IP: {client_ip}")
    return {
        "result": "It was 1951, near the Menlung Basin of Everest. I was wandering through the soft powder, my mind drifting with the clouds. I left wide, heavy tracks—careless, perhaps. I didn't know Eric Shipton was watching from a distance, capturing my footprints in a photograph that would puzzle your world for decades. To me, it was just a morning walk; to him, it was proof of the unknown."
    }


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
            
            # --- FAST PATH ROUTER ---
            fast_response = None
            prompt_lower = prompt.lower()
            
            if "time" in prompt_lower:
                logger.info("⚡  FAST PATH TRIGGERED: TIME")
                try:
                    result = get_current_datetime.invoke({})
                    fast_response = f"The current time is: **{result}**"
                except Exception as e:
                    logger.warning(f"⚠️  Time tool execution failed: {e} -> DEFERRING TO AGENT")
                    fast_response = None
                
            elif "weather" in prompt_lower:
                logger.info("⚡  FAST PATH TRIGGERED: WEATHER")
                
                # Default
                city = "Chiyoda, Tokyo"
                
                # Regex extraction
                match = re.search(r"weather (?:in|for) ([a-zA-Z\s]+)", prompt_lower) 
                if match:
                    city = match.group(1).strip()
                else:
                    match_pre = re.search(r"([a-zA-Z\s]+) weather", prompt_lower)
                    if match_pre:
                         candidate = match_pre.group(1).strip()
                         if candidate not in ["current", "the", "check", "get", "show", "tell me"]:
                             city = candidate

                logger.info(f"📍  EXTRACTED CITY: {city}")
                
                try:
                    data = get_weather.invoke({"city": city})
                    
                    # VALIDATION: Check for tool errors
                    is_error = False
                    if isinstance(data, dict) and data.get("error"):
                        is_error = True
                    elif isinstance(data, str) and "error" in data.lower():
                        is_error = True
                        
                    if is_error:
                         logger.info(f"⚠️  Weather tool returned error for '{city}' -> DEFERRING TO AGENT")
                         fast_response = None
                    else:
                        if isinstance(data, dict) and "location" in data:
                             curr = data['current']
                             fast_response = f"### 🌤️ Weather in {data['location']['name']}\n\n**Temperature:** {curr['temp_c']}°C\n**Condition:** {curr['condition']['text']}\n**Humidity:** {curr['humidity']}%\n**Wind:** {curr['wind_kph']} kph"
                        else:
                            fast_response = str(data)
                except Exception as e:
                    logger.warning(f"⚠️  Weather tool execution failed: {e} -> DEFERRING TO AGENT")
                    fast_response = None

            elif any(x in prompt_lower for x in ["rate", "exchange", "convert", "jpy", "inr", "usd", "eur"]):
                logger.info("⚡  FAST PATH TRIGGERED: EXCHANGE RATE")
                
                from_curr = None
                to_curr = None
                
                # Regex 1
                match = re.search(r"\b([A-Za-z]{3})\b\s+(?:to|in|into)\s+\b([A-Za-z]{3})\b", prompt_lower)
                if match:
                    from_curr = match.group(1).upper()
                    to_curr = match.group(2).upper()
                else:
                    # Regex 2
                    match_lazy = re.search(r"rate\s+\b([A-Za-z]{3})\b\s+\b([A-Za-z]{3})\b", prompt_lower)
                    if match_lazy:
                         from_curr = match_lazy.group(1).upper()
                         to_curr = match_lazy.group(2).upper()

                valid_fast_path = False
                supported_pairs = [
                    # JPY base
                    ("JPY", "NPR"), ("JPY", "INR"), ("JPY", "USD"), ("JPY", "BDT"),
                    ("JPY", "IDR"), ("JPY", "VND"), ("JPY", "PHP"),
                    # CAD base
                    ("CAD", "PHP"), ("CAD", "VND"),
                    # SGD base
                    ("SGD", "PHP"), ("SGD", "VND"),
                    # USD base
                    ("USD", "PHP"), ("USD", "VND")
                ]

                if from_curr and to_curr:
                    if (from_curr, to_curr) in supported_pairs:
                        valid_fast_path = True
                    else:
                        logger.info(f"⚠️  Pair {from_curr}-{to_curr} not in whitelist -> DEFERRING TO AGENT")
                else:
                    logger.info("⚠️  No clear currencies found -> DEFERRING TO AGENT")

                if valid_fast_path:
                    logger.info(f"💱  EXTRACTED PAIR: {from_curr} -> {to_curr}")
                    try:
                        result = get_exchange_rates.invoke({"from_currency": from_curr, "to_currency": to_curr})
                        
                        # Double check the result for error messages
                        if isinstance(result, str) and "Sorry" in result:
                             logger.info("⚠️  Tool logic error -> DEFERRING TO AGENT")
                             fast_response = None
                        elif isinstance(result, dict) and result.get("error"):
                             logger.info("⚠️  Tool error response -> DEFERRING TO AGENT")
                             fast_response = None
                        else:
                            if isinstance(result, dict) and "summary" in result:
                                fast_response = result["summary"]
                            else:
                                fast_response = str(result)
                    except Exception as e:
                        logger.warning(f"⚠️  Exchange tool execution failed: {e} -> DEFERRING TO AGENT")
                        fast_response = None
                else:
                    fast_response = None # Explicitly skip fast path logic

            
            elif "shipton" in prompt_lower or "first encounter" in prompt_lower:
                logger.info("⚡  FAST PATH TRIGGERED: LORE")
                fast_response = "It was 1951, near the Menlung Basin of Everest. I was wandering through the soft powder, my mind drifting with the clouds. I left wide, heavy tracks—careless, perhaps. I didn't know Eric Shipton was watching from a distance, capturing my footprints in a photograph that would puzzle your world for decades. To me, it was just a morning walk; to him, it was proof of the unknown."

            elif "search" in prompt_lower and "digital wallet" in prompt_lower:
                 logger.info("⚡  FAST PATH TRIGGERED: SEARCH DWC")
                 try:
                    result = search_web("Digital Wallet Corporation")
                    if "error" in str(result).lower():
                        logger.info("⚠️  Search tool returned error -> DEFERRING TO AGENT")
                        fast_response = None
                    else:
                        fast_response = result
                 except Exception as e:
                    logger.warning(f"⚠️  Search tool execution failed: {e} -> DEFERRING TO AGENT")
                    fast_response = None


            if fast_response:
                # Simulate a tiny bit of "thinking" time for UX, or just send it
                # For "wow" factor, let's send it instantly but chunked to simulate stream
                # Or just one big chunk. Let's do one big chunk for max speed.
                
                await websocket.send_text(json.dumps({"type": "chunk", "data": fast_response}))
                logger.info(f"✅  FAST RESPONSE SENT | Client #{client_id}")
                print("\n" + "." * 60 + "\n")
                continue # Skip the slow agent loop
            
            # --- SLOW PATH (AGENT) ---
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
