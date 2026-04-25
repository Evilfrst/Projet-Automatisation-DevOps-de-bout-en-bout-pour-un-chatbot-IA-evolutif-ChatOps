from fastapi import FastAPI
from pydantic import BaseModel
from chatbot import get_response

app = FastAPI()

class Message(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"status": "Chatbot API running"}

@app.post("/chat")
def chat(message: Message):
    response = get_response(message.text)
    return {"response": response}
