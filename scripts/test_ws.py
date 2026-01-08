import asyncio
import websockets
import json
import os

async def test_yeti():
    uri = "ws://localhost:8000/ws"
    
    print(f"🏔️  Connecting to Yeti's High Valley at {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")
            
            while True:
                prompt = input("\n👤 You: ")
                if prompt.lower() in ["exit", "quit", "bye"]:
                    break
                
                await websocket.send(prompt)
                
                print("❄️  Yeti: ", end="", flush=True)
                
                while True:
                    try:
                        # Timeout set briefly to check for end of stream if sentinel is missing
                        # but normally the loop breaks on the response object check
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        if data["type"] == "chunk":
                            print(data["data"], end="", flush=True)
                        elif data["type"] == "signal":
                            # We print signals in a different color or brackets
                            print(f"\n[SIGNAL: {data['status']}]", end="\n❄️  Yeti: ", flush=True)
                            
                    except websockets.exceptions.ConnectionClosed:
                        print("\n❌ Connection closed.")
                        return
                    except asyncio.TimeoutError:
                        break
                    except Exception as e:
                        # If the message isn't JSON or other error, break to prompt again
                        break
                print() # New line after response
                
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print("\n💡 Make sure the backend is running (docker compose up).")
        print("💡 You might need to install websockets: 'pip install websockets'")

if __name__ == "__main__":
    try:
        asyncio.run(test_yeti())
    except KeyboardInterrupt:
        print("\n👋 Leaving the mountains. Until next time!")
