from __future__ import annotations

import json
import logging
import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from sqlalchemy import func, or_

from .audit_service import save_audit_log
from .auth import hash_password, verify_password
from .database import SessionLocal, engine
from .kubernetes_service import (
    failed_pods,
    list_deployments,
    list_pods,
    list_services,
    pod_logs,
    restart_deployment,
)
from .models import AuditLog, Base, Conversation, Incident, User
from .permissions import (
    ROLE_DESCRIPTIONS,
    ROLE_PERMISSIONS,
    has_permission,
)
from .prometheus_service import (
    cluster_health,
    cpu_usage,
    memory_usage,
    pod_count,
)
from .rbac import require_permission
from .security import create_access_token, get_current_user


# ==================================================
# CONFIGURATION
# ==================================================

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ChatOps AI Enterprise",
    description="AI DevOps Assistant powered by OpenAI",
    version="2.1.0",
)

Base.metadata.create_all(bind=engine)


# ==================================================
# CORS
# ==================================================

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "https://chatops-ai.fr,http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# PROMETHEUS METRICS
# ==================================================

conversations_saved_total = Counter(
    "conversations_saved_total",
    "Total conversations saved",
)

database_errors_total = Counter(
    "database_errors_total",
    "Total database errors",
)


# ==================================================
# OPENAI
# ==================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY manquante")

openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_pods",
            "description": "Liste tous les pods Kubernetes",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_deployments",
            "description": "Liste tous les deployments Kubernetes",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_services",
            "description": "Liste tous les services Kubernetes",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "failed_pods",
            "description": "Liste les pods Kubernetes en erreur",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cluster_health",
            "description": "Retourne la santé du cluster depuis Prometheus",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pod_logs",
            "description": "Retourne les logs d'un pod Kubernetes",
            "parameters": {
                "type": "object",
                "properties": {
                    "namespace": {"type": "string"},
                    "pod_name": {"type": "string"},
                },
                "required": ["namespace", "pod_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "restart_deployment",
            "description": "Redémarre un deployment Kubernetes",
            "parameters": {
                "type": "object",
                "properties": {
                    "namespace": {"type": "string"},
                    "deployment_name": {"type": "string"},
                },
                "required": ["namespace", "deployment_name"],
            },
        },
    },
]


# ==================================================
# REQUEST MODELS
# ==================================================

class RoleUpdateRequest(BaseModel):
    role: Literal["viewer", "devops", "admin"]


class ChatRequest(BaseModel):
    prompt: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class IncidentCreateRequest(BaseModel):
    title: str
    description: str | None = None
    severity: str = "P3"


class IncidentUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    severity: str | None = None
    status: str | None = None


# ==================================================
# SERIALIZATION HELPERS
# ==================================================

def user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at,
    }


def incident_to_dict(incident: Incident) -> dict:
    return {
        "id": incident.id,
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        "status": incident.status,
        "created_at": incident.created_at,
    }


def safe_monitoring_call(function) -> dict:
    try:
        return {
            "available": True,
            "data": function(),
        }
    except Exception as error:
        logger.warning("Monitoring indisponible pour %s : %s", function.__name__, error)
        return {
            "available": False,
            "error": str(error),
        }


# ==================================================
# PUBLIC ENDPOINTS
# ==================================================

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "ChatOps AI Enterprise",
        "version": "2.1.0",
    }


@app.get("/api/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/register")
def register(data: RegisterRequest):
    username = data.username.strip()
    email = data.email.strip().lower()

    if len(username) < 3:
        raise HTTPException(
            status_code=400,
            detail="Le nom d'utilisateur doit contenir au moins 3 caractères",
        )

    if len(data.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Le mot de passe doit contenir au moins 8 caractères",
        )

    db = SessionLocal()

    try:
        existing_user = (
            db.query(User)
            .filter(
                (User.username == username)
                | (User.email == email)
            )
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Nom d'utilisateur ou adresse e-mail déjà utilisé",
            )

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(data.password),
            role="viewer",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "message": "Utilisateur créé",
            "user": user_to_dict(user),
        }

    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        logger.exception("Erreur lors de l'inscription")
        raise HTTPException(
            status_code=500,
            detail=f"Impossible de créer l'utilisateur : {error}",
        ) from error
    finally:
        db.close()


@app.post("/api/login")
def login(data: LoginRequest):
    """Authentifie un utilisateur sans modifier ses données PostgreSQL.

    Le nom d'utilisateur est comparé sans tenir compte des majuscules,
    minuscules ou espaces accidentels. L'adresse e-mail peut également
    être utilisée. Le rôle et le hash du mot de passe restent inchangés.
    """
    db = SessionLocal()
    identifier = data.username.strip().lower()

    try:
        user = (
            db.query(User)
            .filter(
                or_(
                    func.lower(func.trim(User.username)) == identifier,
                    func.lower(func.trim(User.email)) == identifier,
                )
            )
            .first()
        )

        if user is None:
            logger.warning(
                "Connexion refusée : utilisateur introuvable pour %r",
                data.username.strip(),
            )
            raise HTTPException(
                status_code=401,
                detail="Identifiants incorrects",
            )

        try:
            password_is_valid = verify_password(
                data.password,
                user.password_hash,
            )
        except Exception:
            logger.exception(
                "Format de hash non reconnu pour l'utilisateur %s",
                user.username,
            )
            raise HTTPException(
                status_code=401,
                detail="Identifiants incorrects",
            )

        if not password_is_valid:
            logger.warning(
                "Connexion refusée : mot de passe incorrect pour %s",
                user.username,
            )
            raise HTTPException(
                status_code=401,
                detail="Identifiants incorrects",
            )

        token = create_access_token(
            {
                "sub": user.username,
                "role": user.role,
            }
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "role": user.role,
            "user": user_to_dict(user),
        }

    finally:
        db.close()


# ==================================================
# CURRENT USER AND ROLE MATRIX
# ==================================================

@app.get("/api/me")
def me(current_user: User = Depends(get_current_user)):
    return user_to_dict(current_user)


@app.get("/api/roles")
def roles_matrix(current_user: User = Depends(get_current_user)):
    return {
        role: {
            "description": ROLE_DESCRIPTIONS[role],
            "permissions": sorted(permissions),
        }
        for role, permissions in ROLE_PERMISSIONS.items()
    }


# ==================================================
# INCIDENTS
# ==================================================

@app.post("/api/incidents")
def create_incident(
    data: IncidentCreateRequest,
    current_user: User = Depends(
        require_permission("incidents:create")
    ),
):
    db = SessionLocal()

    try:
        incident = Incident(
            title=data.title.strip(),
            description=data.description,
            severity=data.severity.upper(),
            status="OPEN",
        )

        db.add(incident)
        db.commit()
        db.refresh(incident)

        save_audit_log(
            username=current_user.username,
            action="create_incident",
            target=f"incident_id={incident.id}",
        )

        return incident_to_dict(incident)

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@app.get("/incidents")
def list_incidents(
    current_user: User = Depends(
        require_permission("incidents:read")
    ),
):
    db = SessionLocal()

    try:
        incidents = (
            db.query(Incident)
            .order_by(Incident.id.desc())
            .all()
        )
        return [incident_to_dict(incident) for incident in incidents]
    finally:
        db.close()


@app.patch("/api/incidents/{incident_id}")
def update_incident(
    incident_id: int,
    data: IncidentUpdateRequest,
    current_user: User = Depends(
        require_permission("incidents:update")
    ),
):
    db = SessionLocal()

    try:
        incident = (
            db.query(Incident)
            .filter(Incident.id == incident_id)
            .first()
        )

        if not incident:
            raise HTTPException(
                status_code=404,
                detail="Incident introuvable",
            )

        updates = data.model_dump(exclude_unset=True)

        if "severity" in updates and updates["severity"] is not None:
            updates["severity"] = updates["severity"].upper()

        if "status" in updates and updates["status"] is not None:
            updates["status"] = updates["status"].upper()

        for key, value in updates.items():
            setattr(incident, key, value)

        db.commit()
        db.refresh(incident)

        save_audit_log(
            username=current_user.username,
            action="update_incident",
            target=f"incident_id={incident_id}",
        )

        return incident_to_dict(incident)

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@app.delete("/api/incidents/{incident_id}")
def delete_incident(
    incident_id: int,
    current_user: User = Depends(
        require_permission("incidents:delete")
    ),
):
    db = SessionLocal()

    try:
        incident = (
            db.query(Incident)
            .filter(Incident.id == incident_id)
            .first()
        )

        if not incident:
            raise HTTPException(
                status_code=404,
                detail="Incident introuvable",
            )

        db.delete(incident)
        db.commit()

        save_audit_log(
            username=current_user.username,
            action="delete_incident",
            target=f"incident_id={incident_id}",
        )

        return {"message": "Incident supprimé"}

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ==================================================
# TOOL EXECUTION WITH RBAC
# ==================================================

def execute_function(
    function_name: str,
    arguments: dict | None = None,
    current_user: User | None = None,
):
    username = current_user.username if current_user else "system"
    role = current_user.role if current_user else "viewer"
    arguments = arguments or {}

    tool_permissions = {
        "list_pods": "k8s:diagnose",
        "list_deployments": "k8s:diagnose",
        "list_services": "k8s:diagnose",
        "failed_pods": "k8s:diagnose",
        "pod_logs": "k8s:diagnose",
        "cluster_health": "monitoring:read",
        "restart_deployment": "k8s:restart",
    }

    required_permission = tool_permissions.get(function_name)

    if required_permission and not has_permission(role, required_permission):
        save_audit_log(
            username=username,
            action="permission_denied",
            target=f"{function_name}:{required_permission}",
        )
        raise HTTPException(
            status_code=403,
            detail=(
                "Accès refusé : permission requise "
                f"'{required_permission}'"
            ),
        )

    save_audit_log(
        username=username,
        action=function_name,
    )

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
            arguments["pod_name"],
        )
    if function_name == "restart_deployment":
        return restart_deployment(
            arguments["namespace"],
            arguments["deployment_name"],
        )

    raise HTTPException(
        status_code=400,
        detail=f"Fonction inconnue : {function_name}",
    )


# ==================================================
# CHAT
# ==================================================

@app.post("/api/chat")
async def chat(
    data: ChatRequest,
    current_user: User = Depends(
        require_permission("chat:use")
    ),
):
    prompt = data.prompt.strip()

    if not prompt:
        raise HTTPException(
            status_code=400,
            detail="Le message ne peut pas être vide",
        )

    if not openai_client:
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY non configurée",
        )

    db = SessionLocal()

    try:
        logger.info(
            "Prompt reçu de %s (%s)",
            current_user.username,
            current_user.role,
        )

        response = openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            tools=TOOLS,
            tool_choice="auto",
        )

        message = response.choices[0].message
        tool_calls = getattr(message, "tool_calls", None)

        if tool_calls:
            tool_call = tool_calls[0]
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments or "{}")

            tool_result = execute_function(
                function_name=function_name,
                arguments=arguments,
                current_user=current_user,
            )

            assistant_message = (
                message.model_dump()
                if hasattr(message, "model_dump")
                else {
                    "role": "assistant",
                    "content": getattr(message, "content", ""),
                }
            )

            final_response = openai_client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    },
                    assistant_message,
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(
                            tool_result,
                            ensure_ascii=False,
                            default=str,
                        ),
                    },
                ],
            )

            answer = (
                final_response.choices[0].message.content
                or "Aucune réponse générée"
            )
        else:
            answer = message.content or "Aucune réponse générée"

        conversation = Conversation(
            user_id=current_user.id,
            user_message=prompt,
            ai_response=answer,
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        conversations_saved_total.inc()

        return {
            "response": answer,
            "conversation_id": conversation.id,
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as error:
        db.rollback()
        database_errors_total.inc()
        logger.exception("Erreur du service ChatOps")
        raise HTTPException(
            status_code=500,
            detail=f"Service IA indisponible : {error}",
        ) from error
    finally:
        db.close()


# ==================================================
# HISTORY
# ==================================================

@app.get("/api/history")
def get_history(
    current_user: User = Depends(
        require_permission("history:read:own")
    ),
):
    db = SessionLocal()

    try:
        conversations = (
            db.query(Conversation)
            .filter(Conversation.user_id == current_user.id)
            .order_by(Conversation.id.desc())
            .all()
        )

        return [
            {
                "id": conversation.id,
                "title": (
                    conversation.user_message[:50] + "..."
                    if len(conversation.user_message) > 50
                    else conversation.user_message
                ),
                "user_message": conversation.user_message,
                "ai_response": conversation.ai_response,
                "created_at": conversation.created_at,
            }
            for conversation in conversations
        ]
    finally:
        db.close()


@app.get("/api/history/{conversation_id}")
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(
        require_permission("history:read:own")
    ),
):
    db = SessionLocal()

    try:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation introuvable",
            )

        if (
            conversation.user_id != current_user.id
            and not has_permission(
                current_user.role,
                "history:read:any",
            )
        ):
            raise HTTPException(
                status_code=403,
                detail="Accès refusé",
            )

        return {
            "id": conversation.id,
            "user_id": conversation.user_id,
            "user_message": conversation.user_message,
            "ai_response": conversation.ai_response,
            "created_at": conversation.created_at,
        }
    finally:
        db.close()


# ==================================================
# AUDIT
# ==================================================

@app.get("/api/audit")
def get_audit_logs(
    current_user: User = Depends(
        require_permission("audit:read")
    ),
):
    db = SessionLocal()

    try:
        logs = (
            db.query(AuditLog)
            .order_by(AuditLog.id.desc())
            .all()
        )

        return [
            {
                "id": log.id,
                "username": log.username,
                "action": log.action,
                "target": log.target,
                "created_at": log.created_at,
            }
            for log in logs
        ]
    finally:
        db.close()


# ==================================================
# MONITORING
# ==================================================

@app.get("/api/monitoring/metrics")
def monitoring_metrics(
    current_user: User = Depends(
        require_permission("monitoring:read")
    ),
):
    return {
        "health": safe_monitoring_call(cluster_health),
        "cpu": safe_monitoring_call(cpu_usage),
        "memory": safe_monitoring_call(memory_usage),
        "pods": safe_monitoring_call(pod_count),
    }


@app.get("/api/dashboard/summary")
def dashboard_summary(
    current_user: User = Depends(
        require_permission("monitoring:read")
    ),
):
    return monitoring_metrics(current_user)


# ==================================================
# KUBERNETES
# ==================================================

@app.get("/api/k8s/pods")
def get_pods(
    current_user: User = Depends(
        require_permission("k8s:diagnose")
    ),
):
    return list_pods()


@app.get("/api/k8s/deployments")
def get_deployments(
    current_user: User = Depends(
        require_permission("k8s:diagnose")
    ),
):
    return list_deployments()


@app.get("/api/k8s/services")
def get_services(
    current_user: User = Depends(
        require_permission("k8s:diagnose")
    ),
):
    return list_services()


@app.get("/api/k8s/failed-pods")
def get_failed_pods(
    current_user: User = Depends(
        require_permission("k8s:diagnose")
    ),
):
    return failed_pods()


@app.get("/api/k8s/health")
def kubernetes_health(
    current_user: User = Depends(
        require_permission("k8s:diagnose")
    ),
):
    result = list_pods()

    if isinstance(result, dict) and result.get("error"):
        return {
            "status": "unhealthy",
            "detail": result,
        }

    return {
        "status": "healthy",
        "pods_count": len(result),
    }


@app.get("/api/k8s/logs")
def get_logs(
    namespace: str,
    pod_name: str,
    current_user: User = Depends(
        require_permission("k8s:diagnose")
    ),
):
    return pod_logs(namespace, pod_name)


@app.post("/api/k8s/restart")
def restart(
    namespace: str,
    deployment_name: str,
    current_user: User = Depends(
        require_permission("k8s:restart")
    ),
):
    result = restart_deployment(namespace, deployment_name)

    save_audit_log(
        username=current_user.username,
        action="restart_deployment",
        target=f"{namespace}/{deployment_name}",
    )

    return result


# ==================================================
# USER ADMINISTRATION
# ==================================================

@app.get("/api/admin/users")
def list_users(
    current_user: User = Depends(
        require_permission("users:read")
    ),
):
    db = SessionLocal()

    try:
        users = db.query(User).order_by(User.id.asc()).all()
        return [user_to_dict(user) for user in users]
    finally:
        db.close()


@app.patch("/api/admin/users/{user_id}/role")
def update_user_role(
    user_id: int,
    data: RoleUpdateRequest,
    current_user: User = Depends(
        require_permission("users:role:update")
    ),
):
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="Utilisateur introuvable",
            )

        if user.role == "admin" and data.role != "admin":
            admin_count = (
                db.query(User)
                .filter(User.role == "admin")
                .count()
            )

            if admin_count <= 1:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Impossible de rétrograder "
                        "le dernier administrateur"
                    ),
                )

        previous_role = user.role
        user.role = data.role
        db.commit()
        db.refresh(user)

        save_audit_log(
            username=current_user.username,
            action="update_user_role",
            target=(
                f"user_id={user.id}, "
                f"previous_role={previous_role}, "
                f"new_role={user.role}"
            ),
        )

        return {
            "message": "Rôle mis à jour",
            "user": user_to_dict(user),
        }

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ==================================================
# PROMETHEUS EXPORTER
# ==================================================

Instrumentator().instrument(app).expose(app)
