from fastapi import FastAPI, Request
from app.call_the_model import call_the_model

app = FastAPI()

@app.get("/")
def home():
  return {"response": "Hello world"}

@app.get("/user/{user_id}")
def get_user(user_id: int):
  return {"response", user_id}

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    prompt = body.get("prompt")
    return {"response": call_the_model(prompt)}