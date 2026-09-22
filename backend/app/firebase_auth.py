import json
import os
from pathlib import Path
from typing import Any

import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from fastapi import Header, HTTPException


def _firebase_app() -> firebase_admin.App:
    if firebase_admin._apps:
        return firebase_admin.get_app()
    raw = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    file_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_FILE")
    if raw:
        return firebase_admin.initialize_app(credentials.Certificate(json.loads(raw)))
    if file_path:
        return firebase_admin.initialize_app(credentials.Certificate(Path(file_path)))
    raise HTTPException(status_code=503, detail="Firebase Admin credentials are not configured")


def verify_bearer_token(authorization: str | None) -> dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Firebase bearer token required")
    token = authorization[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Firebase bearer token required")
    try:
        _firebase_app()
        return firebase_auth.verify_id_token(token, check_revoked=True)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired Firebase token") from exc


def get_firebase_claims(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    return verify_bearer_token(authorization)