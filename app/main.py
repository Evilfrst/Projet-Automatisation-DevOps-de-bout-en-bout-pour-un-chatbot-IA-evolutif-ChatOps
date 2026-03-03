
---

### ** Application Code (`app/main.py`)**

This is the enhanced FastAPI application with caching, monitoring, and proper error handling.

```python
import os
import logging
import redis
import openai
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
from dotenv import load_dotenv

# --- Configuration & Initialization ---
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Scalable AI Chatbot",
    description="An AI chatbot with DevOps best practices.",
    version="1.0.0",
)

# Connect to Redis for caching
try:
    redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0)
    redis_client.ping()
    logger.info("Successfully connected to Redis.")
except redis.exceptions.ConnectionError as e:
    logger.error(f"Could not connect to Redis: {e}")
    redis_client = None

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logger.error("OPENAI_API_KEY environment variable not set.")
    # The application will fail at runtime if the key is needed.

# --- Pydantic Models for Request/Response ---
class ChatRequest(BaseModel):
    user_input: str

class ChatResponse(BaseModel):
    bot_response: str
    source: str # To indicate if the response came from cache or the model

# --- Prometheus Metrics ---
Instrumentator().instrument(app).expose(app)

# --- API Endpoints ---
@app.get("/", tags=["Health Check"])
def read_root():
    """Root endpoint for health check."""
    return {"status": "ok", "message": "Welcome to the Chatbot API"}

@app.post("/chat/", response_model=ChatResponse, tags=["Chatbot"])
def chat_with_bot(request: ChatRequest):
    """
    Handles a chat request by fetching a response from cache or the OpenAI API.
    """
    user_input = request.user_input

    # 1. Check cache first
    if redis_client:
        cached_response = redis_client.get(user_input)
        if cached_response:
            logger.info(f"Cache hit for input: '{user_input}'")
            return ChatResponse(
                bot_response=cached_response.decode("utf-8"),
                source="cache"
            )

    logger.info(f"Cache miss for input: '{user_input}'. Querying OpenAI.")

    # 2. If not in cache, call OpenAI API
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key is not configured on the server.")
    
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": user_input}
            ]
        )
        bot_response = completion.choices[0].message.content.strip()

        # 3. Store the new response in cache
        if redis_client:
            # Cache the response for 1 hour (3600 seconds)
            redis_client.setex(user_input, 3600, bot_response)
            logger.info(f"Stored new response in cache for input: '{user_input}'")

        return ChatResponse(bot_response=bot_response, source="model")

    except openai.error.OpenAIError as e:
        logger.error(f"An error occurred with the OpenAI API: {e}")
        raise HTTPException(status_code=503, detail=f"AI service is unavailable: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")
