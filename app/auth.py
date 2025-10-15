from fastapi import Depends, Header, HTTPException, Request
from .config import get_settings


async def verify_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith('bearer '):
        raise HTTPException(status_code=401, detail='Missing or invalid Authorization header')
    token = authorization.split(' ', 1)[1].strip()
    settings = get_settings()
    if token not in settings.valid_client_tokens:
        raise HTTPException(status_code=401, detail='Invalid client token')
    return token


def is_allowed_origin(request: Request) -> bool:
    settings = get_settings()
    if not settings.allowed_origins:
        return True  # allow all if not configured
    origin = request.headers.get('origin') or request.headers.get('referer') or ''
    origin = origin.lower()
    # Basic match: exact or prefix match for scheme+host
    return any(origin.startswith(allowed) for allowed in settings.allowed_origins)


