from fastapi import FastAPI
from pydantic import BaseModel
from chat_chain import get_answer


app = FastAPI(title="Ollama Chat API", version="1.0.0")

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    response = get_answer(req.message)
    return {"response": response}


@app.get("/")
async def root():
    return {"status": "ok", "message": "Welcome to the Ollama Chat API. Use the /chat endpoint to interact."}