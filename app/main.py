from fastapi import FastAPI, Request
from app.call_the_model import call_the_model

app = FastAPI()

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    prompt = body.get("prompt")
    return {"response": call_the_model(prompt)}