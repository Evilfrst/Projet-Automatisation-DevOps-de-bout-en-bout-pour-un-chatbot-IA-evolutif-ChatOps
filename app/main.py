from fastapi import FastAPI
from prometheus_client import Counter, generate_latest
from fastapi.responses import Response

app = FastAPI(
    title="ChatOps AI API",
    version="2.0.0"
)

REQUEST_COUNTER = Counter(
    "chatbot_requests_total",
    "Nombre total de requêtes"
)


@app.get("/")
def root():
    REQUEST_COUNTER.inc()
    return {
        "message": "ChatOps AI API operational"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/chat")
def chat(prompt: str):
    REQUEST_COUNTER.inc()

    return {
        "prompt": prompt,
        "response": f"AI response for: {prompt}"
    }


@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type="text/plain"
    )
