import json
import logging
import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError

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
from .prometheus_service import (
    cluster_health,
    cpu_usage,
    extract_scalar,
    memory_usage,
    pod_count,
)
from .security import create_access_token, get_current_user, require_roles

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ChatOps AI",
    description="Assistant IA pour l'observation et l'exploitation DevOps",
    version="2.1.0",
    root_path=os.getenv("ROOT_PATH", ""),
)

# create_all garde le démarrage local simple. Alembic gère les évolutions de schéma.
Base.metadata.create_all(bind=engine)

conversations_saved_total = Counter(
    "conversations_saved_total", "Total conversations saved"
)
database_errors_total = Counter("database_errors_total", "Total database errors")

raw_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
)
allowed_origins = [
    origin.strip() for origin in raw_origins.split(",") if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY manquante : /chat sera indisponible")

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_pods",
            "description": "Liste les pods Kubernetes dans tous les namespaces",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_deployments",
            "description": "Liste les deployments Kubernetes",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_services",
            "description": "Liste les services Kubernetes",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "failed_pods",
            "description": "Liste les pods qui ne sont ni Running ni Succeeded",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cluster_health",
            "description": "Retourne la disponibilité des cibles Prometheus",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pod_logs",
            "description": "Retourne les 100 dernières lignes de logs d'un pod",
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
            "description": "Redémarre un deployment Kubernetes. Action admin uniquement.",
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


class RoleUpdateRequest(BaseModel):
    role: Literal["viewer", "devops", "admin"]


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=10_000)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class IncidentCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=500)
    description: str | None = Field(default=None, max_length=10_000)
    severity: Literal["P1", "P2", "P3", "P4"] = "P3"


class IncidentUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=500)
    description: str | None = Field(default=None, max_length=10_000)
    severity: Literal["P1", "P2", "P3", "P4"] | None = None
    status: Literal["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"] | None = None


def incident_to_dict(incident: Incident) -> dict:
    return {
        "id": incident.id,
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        "status": incident.status,
        "created_at": incident.created_at,
    }


def execute_function(
    function_name: str,
    arguments: dict | None = None,
    current_user: User | None = None,
):
    arguments = arguments or {}
    username = current_user.username if current_user else "system"
    role = current_user.role if current_user else "viewer"

    read_tools = {
        "list_pods",
        "list_deployments",
        "list_services",
        "failed_pods",
        "pod_logs",
        "cluster_health",
    }

    if function_name in read_tools and role not in {"devops", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cette commande Kubernetes nécessite le rôle devops ou admin",
        )

    if function_name == "restart_deployment" and role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Le redémarrage d'un deployment nécessite le rôle admin",
        )

    functions = {
        "list_pods": lambda: list_pods(),
        "list_deployments": lambda: list_deployments(),
        "list_services": lambda: list_services(),
        "failed_pods": lambda: failed_pods(),
        "cluster_health": lambda: cluster_health(),
        "pod_logs": lambda: pod_logs(arguments["namespace"], arguments["pod_name"]),
        "restart_deployment": lambda: restart_deployment(
            arguments["namespace"], arguments["deployment_name"]
        ),
    }

    if function_name not in functions:
        return {"error": "Function not found"}

    save_audit_log(username=username, action=function_name)
    return functions[function_name]()


def safe_prometheus_value(query_function) -> float | None:
    try:
        return extract_scalar(query_function())
    except Exception as exc:
        logger.warning("Prometheus indisponible : %s", exc)
        return None


def build_dashboard_summary() -> dict:
    pods_result = list_pods()
    failed_result = (
        [pod for pod in pods_result if pod["status"] not in {"Running", "Succeeded"}]
        if isinstance(pods_result, list)
        else pods_result
    )

    if isinstance(pods_result, list):
        pods_total = len(pods_result)
        running_pods = sum(1 for pod in pods_result if pod["status"] == "Running")
        cluster_status = "healthy"
        cluster_error = None
    else:
        pods_total = int(safe_prometheus_value(pod_count) or 0)
        running_pods = 0
        cluster_status = "unavailable"
        cluster_error = pods_result.get("detail") or pods_result.get("error")

    failed_count = len(failed_result) if isinstance(failed_result, list) else 0

    db = SessionLocal()
    try:
        open_incidents = (
            db.query(Incident)
            .filter(Incident.status.in_(["OPEN", "IN_PROGRESS"]))
            .count()
        )
    finally:
        db.close()

    return {
        "cpu": safe_prometheus_value(cpu_usage),
        "memory": safe_prometheus_value(memory_usage),
        "pods": pods_total,
        "running_pods": running_pods,
        "failed_pods": failed_count,
        "open_incidents": open_incidents,
        "cluster_status": cluster_status,
        "cluster_error": cluster_error,
        "cicd": "not_connected",
    }


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "ChatOps AI",
        "version": "2.1.0",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest):
    db = SessionLocal()
    try:
        duplicate = (
            db.query(User)
            .filter((User.username == data.username) | (User.email == data.email))
            .first()
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Nom d'utilisateur ou adresse e-mail déjà utilisé",
            )

        user = User(
            username=data.username.strip(),
            email=data.email.strip().lower(),
            password_hash=hash_password(data.password),
            role="viewer",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"message": "Utilisateur créé", "user_id": user.id}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nom d'utilisateur ou adresse e-mail déjà utilisé",
        )
    finally:
        db.close()


@app.post("/login")
def login(data: LoginRequest):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == data.username).first()
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Identifiants incorrects",
            )

        token = create_access_token(
            {"sub": user.username, "role": user.role, "uid": user.id}
        )
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": user.role,
            "username": user.username,
        }
    finally:
        db.close()


@app.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
    }


@app.post("/chat")
async def chat(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    if not openai_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENAI_API_KEY non configurée",
        )

    prompt = data.prompt.strip()
    logger.info("Prompt reçu de %s", current_user.username)

    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            tools=TOOLS,
            tool_choice="auto",
        )
        message = response.choices[0].message
        tool_calls = getattr(message, "tool_calls", None) or []

        if tool_calls:
            tool_messages = []
            for tool_call in tool_calls:
                try:
                    arguments = json.loads(tool_call.function.arguments or "{}")
                except json.JSONDecodeError:
                    arguments = {}

                result = execute_function(
                    tool_call.function.name,
                    arguments,
                    current_user=current_user,
                )
                tool_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, ensure_ascii=False, default=str),
                    }
                )

            assistant_message = (
                message.model_dump(exclude_none=True)
                if hasattr(message, "model_dump")
                else {"role": "assistant", "content": message.content or ""}
            )
            final_response = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "user", "content": prompt},
                    assistant_message,
                    *tool_messages,
                ],
            )
            answer = final_response.choices[0].message.content
        else:
            answer = message.content

        answer = answer or "Aucune réponse générée"
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Erreur du service IA")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Service IA indisponible : {exc}",
        ) from exc

    db = SessionLocal()
    try:
        conversation = Conversation(
            user_id=current_user.id,
            user_message=prompt,
            ai_response=answer,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        conversations_saved_total.inc()
    except Exception as exc:
        db.rollback()
        database_errors_total.inc()
        logger.exception("La conversation n'a pas pu être sauvegardée")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Réponse générée, mais sauvegarde de l'historique impossible. "
                "Exécutez les migrations Alembic."
            ),
        ) from exc
    finally:
        db.close()

    return {
        "response": answer,
        "conversation_id": conversation.id,
        "saved": True,
    }


@app.get("/history")
def get_history(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        conversations = (
            db.query(Conversation)
            .filter(Conversation.user_id == current_user.id)
            .order_by(Conversation.created_at.desc(), Conversation.id.desc())
            .all()
        )
        return [
            {
                "id": item.id,
                "title": (
                    item.user_message[:50] + "..."
                    if len(item.user_message) > 50
                    else item.user_message
                ),
                "user_message": item.user_message,
                "ai_response": item.ai_response,
                "created_at": item.created_at,
            }
            for item in conversations
        ]
    finally:
        db.close()


@app.get("/history/{conversation_id}")
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
):
    db = SessionLocal()
    try:
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id,
            )
            .first()
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation introuvable")
        return {
            "id": conversation.id,
            "user_message": conversation.user_message,
            "ai_response": conversation.ai_response,
            "created_at": conversation.created_at,
        }
    finally:
        db.close()


@app.post("/incidents", status_code=status.HTTP_201_CREATED)
def create_incident(
    data: IncidentCreateRequest,
    current_user: User = Depends(require_roles("devops", "admin")),
):
    db = SessionLocal()
    try:
        incident = Incident(**data.model_dump(), status="OPEN")
        db.add(incident)
        db.commit()
        db.refresh(incident)
        save_audit_log(
            current_user.username, "create_incident", f"incident_id={incident.id}"
        )
        return incident_to_dict(incident)
    finally:
        db.close()


@app.get("/incidents")
def get_incidents(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        incidents = db.query(Incident).order_by(Incident.id.desc()).all()
        return [incident_to_dict(item) for item in incidents]
    finally:
        db.close()


@app.patch("/incidents/{incident_id}")
def update_incident(
    incident_id: int,
    data: IncidentUpdateRequest,
    current_user: User = Depends(require_roles("devops", "admin")),
):
    db = SessionLocal()
    try:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise HTTPException(status_code=404, detail="Incident introuvable")

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(incident, key, value)
        db.commit()
        db.refresh(incident)
        save_audit_log(
            current_user.username, "update_incident", f"incident_id={incident_id}"
        )
        return incident_to_dict(incident)
    finally:
        db.close()


@app.delete("/incidents/{incident_id}")
def delete_incident(
    incident_id: int,
    current_user: User = Depends(require_roles("admin")),
):
    db = SessionLocal()
    try:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise HTTPException(status_code=404, detail="Incident introuvable")
        db.delete(incident)
        db.commit()
        save_audit_log(
            current_user.username, "delete_incident", f"incident_id={incident_id}"
        )
        return {"message": "Incident supprimé"}
    finally:
        db.close()


@app.get("/audit")
def get_audit_logs(current_user: User = Depends(require_roles("admin"))):
    db = SessionLocal()
    try:
        logs = db.query(AuditLog).order_by(AuditLog.id.desc()).all()
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


@app.get("/k8s/pods")
def get_pods(current_user: User = Depends(require_roles("devops", "admin"))):
    return list_pods()


@app.get("/k8s/deployments")
def get_deployments(
    current_user: User = Depends(require_roles("devops", "admin")),
):
    return list_deployments()


@app.get("/k8s/services")
def get_services(current_user: User = Depends(require_roles("devops", "admin"))):
    return list_services()


@app.get("/k8s/failed-pods")
def get_failed_pods(
    current_user: User = Depends(require_roles("devops", "admin")),
):
    return failed_pods()


@app.get("/k8s/logs")
def get_logs(
    namespace: str,
    pod_name: str,
    current_user: User = Depends(require_roles("devops", "admin")),
):
    return pod_logs(namespace, pod_name)


@app.post("/k8s/restart")
def restart(
    namespace: str,
    deployment_name: str,
    current_user: User = Depends(require_roles("admin")),
):
    save_audit_log(
        current_user.username,
        "restart_deployment",
        f"{namespace}/{deployment_name}",
    )
    return restart_deployment(namespace, deployment_name)


@app.get("/k8s/health")
def kubernetes_health(
    current_user: User = Depends(require_roles("devops", "admin")),
):
    pods = list_pods()
    if not isinstance(pods, list):
        raise HTTPException(status_code=503, detail=pods)
    return {
        "status": "healthy",
        "pods_count": len(pods),
        "running_pods": sum(1 for pod in pods if pod["status"] == "Running"),
    }


@app.get("/dashboard/summary")
def dashboard_summary(current_user: User = Depends(get_current_user)):
    return build_dashboard_summary()


@app.get("/monitoring/metrics")
def monitoring_metrics(current_user: User = Depends(get_current_user)):
    """Alias conservé pour compatibilité avec les anciennes versions du frontend."""
    return build_dashboard_summary()


@app.get("/admin/users")
def list_users(current_user: User = Depends(require_roles("admin"))):
    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.id.asc()).all()
        return [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at,
            }
            for user in users
        ]
    finally:
        db.close()


@app.patch("/admin/users/{user_id}/role")
def update_user_role(
    user_id: int,
    data: RoleUpdateRequest,
    current_user: User = Depends(require_roles("admin")),
):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur introuvable")
        user.role = data.role
        db.commit()
        db.refresh(user)
        save_audit_log(
            current_user.username,
            "update_user_role",
            f"user_id={user_id}, role={data.role}",
        )
        return {"message": "Rôle mis à jour", "user_id": user.id, "role": user.role}
    finally:
        db.close()


Instrumentator().instrument(app).expose(app)
