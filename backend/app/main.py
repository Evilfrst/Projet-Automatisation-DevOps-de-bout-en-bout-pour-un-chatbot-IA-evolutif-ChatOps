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
import json

from .kubernetes_service import (
    list_pods,
    list_deployments,
    list_services,
    failed_pods,
    pod_logs,
    restart_deployment
)
from .aws_service import list_ec2
from .prometheus_service import cluster_health


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
# TOOLS OPENAI
# ==================================================

TOOLS = [

    {
        "type": "function",
        "function": {
            "name": "list_pods",
            "description": "Liste tous les pods Kubernetes"
        }
    },

    {
        "type": "function",
        "function": {
            "name": "list_ec2",
            "description": "Liste les instances EC2 AWS"
        }
    },

    {
        "type": "function",
        "function": {
            "name": "cluster_health",
            "description": "Retourne la santé du cluster Prometheus"
        }
    }
{
    "type": "function",
    "function": {
        "name": "list_deployments",
        "description": "Liste tous les deployments Kubernetes"
    }
}
{
    "type": "function",
    "function": {
        "name": "list_services",
        "description": "Liste tous les services Kubernetes"
    }
},
{
    "type": "function",
    "function": {
        "name": "failed_pods",
        "description": "Liste les pods en erreur"
    }
}
]
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

def execute_function(function_name):

    if function_name == "list_pods":
        return list_pods()

    elif function_name == "list_deployments":
        return list_deployments()

    elif function_name == "list_services":
        return list_services()

    elif function_name == "failed_pods":
        return failed_pods()

    elif function_name == "cluster_health":
        return cluster_health()

    elif function_name == "list_ec2":
        return list_ec2()

    return {
        "error": "Unknown function"
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
            tools=TOOLS,
            tool_choice="auto"
        )

        answer = response.choices[0].message
        if message.tool_calls:

    tool_call = message.tool_calls[0]

    function_name = tool_call.function.name

    logger.info(
        f"Tool appelé : {function_name}"
    )

    tool_result = execute_function(
        function_name
    )

    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[

            {
                "role": "user",
                "content": data.prompt
            },

            message,

            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result)
            }

        ]
    )

    answer = (
        final_response
        .choices[0]
        .message
        .content
    )

else:

    answer = message.content

        try:

            conversation = Conversation(
                user_message=data.prompt,
                ai_response=answer
            )

            db.add(conversation)
            db.commit()

            conversations_saved_total.inc()

            logger.info(
                f"Conversation sauvegardée ID={conversation.id}"
            )

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

        conversations = (
            db.query(Conversation)
            .order_by(Conversation.id.desc())
            .all()
        )

        return [
            {
                "id": c.id,
                "title": (
                    c.user_message[:50] + "..."
                    if len(c.user_message) > 50
                    else c.user_message
                ),
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
# GET ONE CONVERSATION
# ==================================================

@app.get("/history/{conversation_id}")
def get_conversation(conversation_id: int):

    db = SessionLocal()

    try:

        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id
            )
            .first()
        )

        if not conversation:

            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )

        return {
            "id": conversation.id,
            "user_message": conversation.user_message,
            "ai_response": conversation.ai_response
        }

    finally:

        db.close()
        
# ==================================================
# REST
# ==================================================

@app.get("/monitoring/metrics")
def monitoring_metrics():

    return {
        "health": cluster_health(),
        "cpu": cpu_usage(),
        "memory": memory_usage(),
        "pods": pod_count()
    }
@app.get("/k8s/pods")
def get_pods():
    return list_pods()


@app.get("/k8s/deployments")
def get_deployments():
    return list_deployments()


@app.get("/k8s/services")
def get_services():
    return list_services()


@app.get("/k8s/failed-pods")
def get_failed_pods():
    return failed_pods()

# ==================================================
# PROMETHEUS
# ==================================================

Instrumentator().instrument(app).expose(app)
