from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from prometheus_fastapi_instrumentator import Instrumentator
from openai import OpenAI

import os
import logging


# ==================================================
# LOAD ENV VARIABLES
# ==================================================

load_dotenv()


# ==================================================
# LOGGING
# ==================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ==================================================
# FASTAPI APP
# ==================================================

app = FastAPI(
    title="ChatOps AI Enterprise",
    description="AI DevOps Assistant powered by OpenAI",
    version="2.0.0"
)


# ==================================================
# CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# OPENAI CONFIG
# ==================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
   OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "test-key")

client = OpenAI(
    api_key=OPENAI_API_KEY
)


# ==================================================
# REQUEST MODEL
# ==================================================

class ChatRequest(BaseModel):

    prompt: str

# ==================================================
# ROOT ENDPOINT
# ==================================================

@app.get("/")
async def root():

    return {
        "status": "online",
        "service": "ChatOps AI Enterprise",
        "version": "2.0.0"
    }


# ==================================================
# HEALTHCHECK
# ==================================================

@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }


# ==================================================
# CHAT ENDPOINT
# ==================================================

@app.post("/chat")
async def chat(data: ChatRequest):

    return {
        "response": f"Hello {data.prompt}"
    }
    
@app.get("/")
async def root():
         return {"status": "running"}

@app.get("/health")
async def health():
         return {"health": "ok"}

Instrumentator().instrument(app).expose(app)
