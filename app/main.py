from fastapi import FastAPI
from pydantic import BaseModel
from commands import handle_command

app = FastAPI()

class Command(BaseModel):
    text: str

@app.post("/command")
def command(cmd: Command):
    return {"response": handle_command(cmd.text)}

@app.get("/health")
def health():
    return {"status": "ok"}
