from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from fastapi import HTTPException, Request
import jwt


SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


@dataclass(frozen=True)
class CurrentUser:
    subject: str
    username: str
    email: str | None
    name: str | None
    groups: tuple[str, ...]
    roles: tuple[str, ...]
    auth_type: str

    @property
    def is_service(self) -> bool:
        return self.auth_type == "service-token"


def auth_api_required() -> bool:
    return os.getenv("AUTH_API_REQUIRED", "false").lower() in {"1", "true", "yes", "on"}


def write_roles() -> set[str]:
    configured = os.getenv("AUTH_WRITE_ROLES", "admin,operator")
    return {role.strip() for role in configured.split(",") if role.strip()}


def service_token() -> str | None:
    token = os.getenv("AUTH_SERVICE_TOKEN", "").strip()
    return token or None


def oidc_jwks_url() -> str | None:
    value = os.getenv("AUTH_OIDC_JWKS_URL", "").strip()
    return value or None


@lru_cache(maxsize=4)
def _jwk_client(jwks_url: str) -> jwt.PyJWKClient:
    return jwt.PyJWKClient(jwks_url)


def _split_claims(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    separators = [",", "|", ";"]
    values = [value]
    for separator in separators:
        values = [item for chunk in values for item in chunk.split(separator)]
    return tuple(item.strip() for item in values if item.strip())


def _bearer_token(request: Request) -> str | None:
    authorization = request.headers.get("authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() == "bearer" and token:
        return token.strip()
    return None


def _current_user_from_jwt(token: str) -> CurrentUser | None:
    jwks_url = oidc_jwks_url()
    if not jwks_url:
        return None
    try:
        signing_key = _jwk_client(jwks_url).get_signing_key_from_jwt(token)
        options = {"verify_aud": bool(os.getenv("AUTH_OIDC_AUDIENCE", "").strip())}
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "ES256"],
            audience=os.getenv("AUTH_OIDC_AUDIENCE", "").strip() or None,
            issuer=os.getenv("AUTH_OIDC_ISSUER", "").strip() or None,
            options=options,
        )
    except jwt.PyJWTError:
        return None
    groups_value = claims.get("groups") or claims.get("ak_proxy", {}).get("groups") or ()
    roles_value = claims.get("roles") or claims.get("scope") or groups_value
    groups = tuple(groups_value) if isinstance(groups_value, list) else _split_claims(str(groups_value))
    roles = tuple(roles_value) if isinstance(roles_value, list) else _split_claims(str(roles_value))
    return CurrentUser(
        subject=str(claims.get("sub") or "jwt:unknown"),
        username=str(claims.get("preferred_username") or claims.get("email") or claims.get("sub") or "jwt-user"),
        email=claims.get("email"),
        name=claims.get("name"),
        groups=groups,
        roles=roles or groups,
        auth_type="jwt",
    )


def current_user_from_request(request: Request) -> CurrentUser | None:
    token = _bearer_token(request)
    configured_token = service_token()
    if configured_token and token == configured_token:
        return CurrentUser(
            subject="service:internal",
            username="internal-service",
            email=None,
            name="Internal service",
            groups=("service",),
            roles=("service", "admin"),
            auth_type="service-token",
        )
    if token:
        user = _current_user_from_jwt(token)
        if user is not None:
            return user

    username = request.headers.get("x-authentik-username") or request.headers.get("x-forwarded-user")
    email = request.headers.get("x-authentik-email") or request.headers.get("x-forwarded-email")
    subject = request.headers.get("x-authentik-uid") or request.headers.get("x-authentik-sub") or email or username
    if not username and not subject:
        return None

    groups = _split_claims(request.headers.get("x-authentik-groups") or request.headers.get("x-forwarded-groups"))
    roles = _split_claims(request.headers.get("x-authentik-roles") or request.headers.get("x-forwarded-roles"))
    if not roles:
        roles = groups
    return CurrentUser(
        subject=subject or username or "unknown",
        username=username or email or subject or "unknown",
        email=email,
        name=request.headers.get("x-authentik-name") or request.headers.get("x-forwarded-name"),
        groups=groups,
        roles=roles,
        auth_type="proxy",
    )


def require_current_user(request: Request) -> CurrentUser:
    user = current_user_from_request(request)
    if user is not None:
        return user
    if not auth_api_required():
        return CurrentUser(
            subject="local:anonymous",
            username="local-anonymous",
            email=None,
            name="Local anonymous user",
            groups=("admin",),
            roles=("admin",),
            auth_type="disabled",
        )
    raise HTTPException(status_code=401, detail="Authentication required")


def require_write_access(request: Request) -> None:
    if request.method in SAFE_METHODS:
        return
    user = require_current_user(request)
    if user.is_service or set(user.roles) & write_roles():
        return
    raise HTTPException(status_code=403, detail="Write permission required")
