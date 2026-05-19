from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
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
    raise Exception(
        "OPENAI_API_KEY est manquante dans le fichier .env"
    )

client = OpenAI(
    api_key=OPENAI_API_KEY
)


# ==================================================
# REQUEST MODEL
# ==================================================

class ChatRequest(BaseModel):

    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Message utilisateur"
    )


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

        user_message = data.message

        logger.info(f"New message received : {user_message}")

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        ai_response = response.choices[0].message.content

        logger.info("OpenAI response generated successfully")

        return {
            "success": True,
            "response": ai_response
        }

    except Exception as e:

        logger.error(f"ERREUR OPENAI : {str(e)}")

        return {
            "success": False,
            "response": f"Erreur OpenAI : {str(e)}"
        }
    
@app.get("/")
async def root():
         return {"status": "running"}

@app.get("/health")
async def health():
         return {"health": "ok"}

Instrumentator().instrument(app).expose(app)