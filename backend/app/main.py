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
   raise ValueError("OPENAI_API_KEY manquante")

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

    try:

        if not OPENAI_API_KEY:

            return {
                "response": f"Mock response: {data.prompt}"
            }

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": data.prompt
                }
            ]
        )

        return {
            "response": response.choices[0].message.content
        }

    except Exception as e:

        logger.error(str(e))

        return {
            "response": "AI service unavailable"
        }
    
@app.get("/")
async def root():
         return {"status": "running"}

@app.get("/health")
async def health():
         return {"health": "ok"}

Instrumentator().instrument(app).expose(app)
