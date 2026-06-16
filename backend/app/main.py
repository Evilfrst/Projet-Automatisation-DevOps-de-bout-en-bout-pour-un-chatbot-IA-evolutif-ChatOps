from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter
from openai import OpenAI
from .auth import hash_password, verify_password
from .security import create_access_token
from .models import User
from .audit_service import save_audit_log

from .database import SessionLocal, engine
from .models import Conversation, Base

from .kubernetes_service import (
    list_pods,
    list_deployments,
    list_services,
    failed_pods,
    pod_logs,
    restart_deployment
)

from .prometheus_service import (
    cluster_health,
    cpu_usage,
    memory_usage,
    pod_count
)

import os
import json
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
# OPENAI TOOLS
# ==================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_pods",
            "description": "Liste tous les pods Kubernetes",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_deployments",
            "description": "Liste tous les deployments Kubernetes",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_services",
            "description": "Liste tous les services Kubernetes",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "failed_pods",
            "description": "Liste les pods en erreur",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cluster_health",
            "description": "Retourne la santé du cluster Prometheus",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "pod_logs",
        "description": "Retourne les logs d'un pod Kubernetes",
        "parameters": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string"
                },
                "pod_name": {
                    "type": "string"
                }
            },
            "required": [
                "namespace",
                "pod_name"
            ]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "restart_deployment",
        "description": "Redémarre un deployment Kubernetes",
        "parameters": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string"
                },
                "deployment_name": {
                    "type": "string"
                }
            },
            "required": [
                "namespace",
                "deployment_name"
            ]
        }
    }
}
]


# ==================================================
# REQUEST MODEL
# ==================================================
class ChatRequest(BaseModel):
    prompt: str
    
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str

# ==================================================
# REGISTER
# ==================================================

@app.post("/register")
def register(data: RegisterRequest):

    db = SessionLocal()

    try:

        existing_user = (
            db.query(User)
            .filter(User.username == data.username)
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Utilisateur déjà existant"
            )

        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(
                data.password
            ),
            role="viewer"
        )

        db.add(user)
        db.commit()

        return {
            "message": "Utilisateur créé"
        }

    finally:
        db.close()


@app.post("/login")
def login(data: LoginRequest):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.username == data.username)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Utilisateur inconnu"
            )

        if not verify_password(
            data.password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=401,
                detail="Mot de passe incorrect"
            )

        token = create_access_token(
            {
                "sub": user.username,
                "role": user.role
            }
        )

        return {
            "access_token": token,
            "role": user.role
        }

    finally:
        db.close()


# ==================================================
# TOOL EXECUTION
# ==================================================

def execute_function(
    function_name,
    arguments=None,
    username="system"
):

    save_audit_log(
        username=username,
        action=function_name
    )

    arguments = arguments or {}

    if function_name == "list_pods":
        return list_pods()

    if function_name == "list_deployments":
        return list_deployments()

    if function_name == "list_services":
        return list_services()

    if function_name == "failed_pods":
        return failed_pods()

    if function_name == "cluster_health":
        return cluster_health()

    if function_name == "pod_logs":

        return pod_logs(
            arguments["namespace"],
            arguments["pod_name"]
        )

    if function_name == "restart_deployment":

        return restart_deployment(
            arguments["namespace"],
            arguments["deployment_name"]
        )

    return {
        "error": "Function not found"
    }

# ==================================================
# AUDIT ENDPOINT
# ==================================================

@app.get("/audit")
def get_audit_logs():

    db = SessionLocal()

    try:

        logs = (
            db.query(AuditLog)
            .order_by(
                AuditLog.id.desc()
            )
            .all()
        )

        return [
            {
                "id": log.id,
                "username": log.username,
                "action": log.action,
                "target": log.target,
                "created_at": log.created_at
            }
            for log in logs
        ]

    finally:
        db.close()


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
            tools=TOOLS,
            tool_choice="auto"
        )

        message = response.choices[0].message

        tool_calls = getattr(
            message,
            "tool_calls",
            None
        )

        if tool_calls:

            tool_call = tool_calls[0]

            function_name = tool_call.function.name
            arguments = json.loads(
            tool_call.function.arguments
            )

            logger.info(
                f"Tool appelé : {function_name}"
            )

            tool_result = execute_function(
                function_name,
                arguments
            )

            final_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": data.prompt
                    },
                    (
                        message.model_dump()
                        if hasattr(message, "model_dump")
                        else {
                            "role": "assistant",
                            "content": getattr(
                                message,
                                "content",
                                ""
                            )
                        }
                    ),
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result)
                    }
                ]
            )

            answer = getattr(
                final_response.choices[0].message,
                "content",
                "Aucune réponse générée"
            )

        else:

            answer = getattr(
                message,
                "content",
                "Aucune réponse générée"
            )

        try:

            conversation = Conversation(
                user_id=current_user.id,
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

    finally:

        db.close()


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
# KUBERNETES REST API
# ==================================================

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


@app.get("/k8s/health")
def kubernetes_health():

    try:

        pods = list_pods()

        return {
            "status": "healthy",
            "pods_count": len(pods)
        }

    except Exception as e:

        return {
            "status": "unhealthy",
            "error": str(e)
        }
        
@app.get("/k8s/logs")
def get_logs(
    namespace: str,
    pod_name: str
):

    return pod_logs(
        namespace,
        pod_name
    )

@app.post("/k8s/restart")
def restart(
    namespace: str,
    deployment_name: str
):

    return restart_deployment(
        namespace,
        deployment_name
    )
# ==================================================
# MONITORING
# ==================================================

@app.get("/monitoring/metrics")
def monitoring_metrics():

    return {
        "health": cluster_health(),
        "cpu": cpu_usage(),
        "memory": memory_usage(),
        "pods": pod_count()
    }


# ==================================================
# PROMETHEUS EXPORTER
# ==================================================

Instrumentator().instrument(app).expose(app)
