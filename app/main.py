from fastapi import FastAPI
from pydantic import BaseModel
from chatbot import get_response

from prometheus_client import Counter, generate_latest
from fastapi.responses import Response

app = FastAPI()

# 📊 Metrics
REQUEST_COUNT = Counter("app_requests_total", "Total requests")

class Message(BaseModel):
    text: str

@app.get("/")
def read_root():
    REQUEST_COUNT.inc()
    return {"status": "Chatbot API running"}

@app.post("/chat")
def chat(message: Message):
    REQUEST_COUNT.inc()
    response = get_response(message.text)
    return {"response": response}

from prometheus_client import Histogram

REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency")

@app.post("/chat")
def chat(message: Message):
    with REQUEST_LATENCY.time():
        response = get_response(message.text)
    return {"response": response}

# 🔥 Endpoint Prometheus
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
