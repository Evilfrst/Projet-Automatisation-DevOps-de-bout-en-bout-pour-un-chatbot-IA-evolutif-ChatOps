from __future__ import annotations


ROLE_PERMISSIONS: dict[str, set[str]] = {
    "viewer": {
        "chat:use",
        "history:read:own",
        "incidents:read",
    },

    "devops": {
        # Droits du viewer
        "chat:use",
        "history:read:own",
        "incidents:read",

        # Droits DevOps
        "incidents:create",
        "incidents:update",
        "k8s:diagnose",
        "monitoring:read",
    },

    "admin": {
        # Droits généraux
        "chat:use",
        "history:read:own",
        "history:read:any",

        # Incidents
        "incidents:read",
        "incidents:create",
        "incidents:update",
        "incidents:delete",

        # Kubernetes et monitoring
        "k8s:diagnose",
        "k8s:restart",
        "monitoring:read",

        # Administration
        "audit:read",
        "users:read",
        "users:role:update",
    },
}


ROLE_DESCRIPTIONS: dict[str, str] = {
    "viewer": (
        "Chat, historique personnel et consultation des incidents"
    ),

    "devops": (
        "Droits viewer, diagnostics Kubernetes, monitoring, "
        "création et modification d'incidents"
    ),

    "admin": (
        "Droits complets, redémarrage, suppression, audit "
        "et gestion des rôles"
    ),
}


def has_permission(role: str, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())
