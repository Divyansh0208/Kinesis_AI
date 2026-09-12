"""
Firebase Admin SDK init. Server-side only — used to verify ID tokens
the frontend gets from Firebase Auth (email/password + Google).

Env vars needed:
  FIREBASE_CREDENTIALS_PATH  -> path to service-account JSON (Firebase Console
                                 > Project Settings > Service Accounts > Generate key)

Web config (public, safe to expose to browser) needed for the frontend SDK:
  FIREBASE_API_KEY
  FIREBASE_AUTH_DOMAIN
  FIREBASE_PROJECT_ID
  FIREBASE_APP_ID
"""
import os
import logging

import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

logger = logging.getLogger(__name__)

_initialized = False


def init_firebase():
    global _initialized
    if _initialized or firebase_admin._apps:
        _initialized = True
        return

    cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH")
    if not cred_path or not os.path.exists(cred_path):
        raise RuntimeError(
            "FIREBASE_CREDENTIALS_PATH is not set or file not found. "
            "Download the service-account JSON from Firebase Console > "
            "Project Settings > Service Accounts, and set the env var to its path."
        )

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    _initialized = True
    logger.info("Firebase Admin SDK initialized.")


def verify_id_token(id_token: str) -> dict:
    """Verify a Firebase ID token from the client. Raises on invalid/expired token."""
    return firebase_auth.verify_id_token(id_token)


def get_web_config() -> dict:
    """Public web config for the frontend Firebase JS SDK. Safe to expose."""
    return {
        "apiKey": os.environ.get("FIREBASE_API_KEY", ""),
        "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN", ""),
        "projectId": os.environ.get("FIREBASE_PROJECT_ID", ""),
        "appId": os.environ.get("FIREBASE_APP_ID", ""),
    }
