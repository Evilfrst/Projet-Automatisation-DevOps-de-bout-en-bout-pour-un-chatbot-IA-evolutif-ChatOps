from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter
from openai import OpenAI

from .database import SessionLocal, engine
from .models import Conversation, Base

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
# DATABASE INIT
# ==================================================

Base.metadata.create_all(bind=engine)


# ==================================================
# PROMETHEUS METRICS
# ==================================================

conversations_saved_total = Counter(
    "conversations_saved_total",
    "Total conversations saved"
)

database_errors_total = Counter(
    "database_errors_total",
    "Total database errors"
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
    logger.warning("OPENAI_API_KEY manquante")

client = None

if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)


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

    db = SessionLocal()

    try:

        if not client:
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEY not configured"
            )

        logger.info(f"Prompt reçu : {data.prompt}")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": data.prompt
                }
            ],
            temperature=0.7,
            max_tokens=300
        )

        answer = response.choices[0].message.content

        # ==========================================
        # SAVE CONVERSATION
        # ==========================================

        try:

            conversation = Conversation(
                user_message=data.prompt,
                ai_response=answer
            )

            db.add(conversation)
            db.commit()

            conversations_saved_total.inc()

            logger.info("Conversation sauvegardée")

        except Exception as db_error:

            db.rollback()

            database_errors_total.inc()

            logger.warning(
                f"Impossible de sauvegarder la conversation : {db_error}"
            )

        return {
            "response": answer
        }

    except HTTPException as http_error:

        logger.error(str(http_error.detail))
        raise http_error

    except Exception as e:

        logger.exception("Erreur OpenAI")

        raise HTTPException(
            status_code=500,
            detail=f"AI service unavailable: {str(e)}"
        )

    finally:

        db.close()


# ==================================================
# HISTORY ENDPOINT
# ==================================================

@app.get("/history")
def get_history():

    db = SessionLocal()

    try:

        conversations = db.query(Conversation).all()

        return [
            {
                "id": c.id,
                "user_message": c.user_message,
                "ai_response": c.ai_response
            }
            for c in conversations
        ]

    except Exception as e:

        logger.warning(
            f"Historique indisponible : {e}"
        )

        return []

    finally:

        db.close()


# ==================================================
# PROMETHEUS
# ==================================================

Instrumentator().instrument(app).expose(app)
