from dataclasses import dataclass
from uuid import UUID

from fastapi import Header, HTTPException, status


@dataclass
class UserContext:
    subject: str
    user_id: UUID | None = None
    tenant_id: UUID | None = None
    roles: list[str] | None = None


async def get_current_user(
    authorization: str | None = Header(default=None),
) -> UserContext:
    """Dev stub: accept missing auth in local development.

    Production services must validate Keycloak JWTs at the boundary.
    """
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
        return UserContext(subject=token[:32] or "anonymous", roles=["developer"])
    # Allow unauthenticated local bootstrap so the skeleton boots without Keycloak.
    return UserContext(subject="local-dev", roles=["developer"])


def require_role(user: UserContext, role: str) -> None:
    roles = user.roles or []
    if role not in roles and "developer" not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
