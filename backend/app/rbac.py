from __future__ import annotations

from fastapi import Depends, HTTPException, status

from .models import User
from .permissions import has_permission
from .security import get_current_user


def require_permission(permission: str):
    """
    Vérifie que l'utilisateur connecté possède
    la permission demandée.
    """

    def permission_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:

        if not has_permission(
            current_user.role,
            permission
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Accès refusé : permission requise "
                    f"'{permission}'"
                ),
            )

        return current_user

    return permission_checker
