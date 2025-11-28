import os
import json
import logging
from pathlib import Path

import firebase_admin
from firebase_admin import credentials

logger = logging.getLogger(__name__)

# Determine a sensible list of candidate paths for the Service Account JSON
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = os.getenv("FIREBASE_SERVICE_ACCOUNT")
candidate_paths = []
if env_path:
    candidate_paths.append(Path(env_path))

# Common paths that may contain the service account key
candidate_paths.extend([
    BASE_DIR / "firebase" / "serviceAccountKey.json",
    BASE_DIR / "serviceAccountKey.json",
    BASE_DIR / "firebase_service_account.json",
    Path("/etc/secrets/serviceAccountKey.json"),
])


def _load_cred_from_env_string() -> credentials.Certificate | None:
    """If the service account JSON is provided directly as an environment string, load it."""
    env_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if not env_json:
        return None

    try:
        # Parse as JSON and write to a temporary file
        data = json.loads(env_json)
        return credentials.Certificate(data)
    except Exception as exc:
        logger.exception("Failed to parse FIREBASE_SERVICE_ACCOUNT_JSON: %s", exc)
        return None


def init_firebase():
    """Safe initializer for Firebase Admin SDK.

    Tries to initialize using several locations where a service account may be stored.
    This function is safe to call multiple times; the SDK will be initialized only once.
    """
    try:
        # If already initialized, don't do anything
        firebase_admin.get_app()
        logger.debug("Firebase app already initialized")
        return firebase_admin
    except ValueError:
        # Not initialized yet; proceed to try credential loading
        pass

    # 1) Check if a full JSON string is in environment
    env_cred = _load_cred_from_env_string()
    if env_cred:
        firebase_admin.initialize_app(env_cred)
        logger.info("✅ Firebase initialized from FIREBASE_SERVICE_ACCOUNT_JSON env var")
        return firebase_admin

    # 2) Check filesystem candidate paths
    for p in candidate_paths:
        try:
            p = Path(p)
            if p.exists():
                # Basic content validation: ensure it parses as JSON and has required keys
                try:
                    # Try multiple encodings to be robust for different editors or BOMs
                    text = None
                    for enc in ("utf-8", "utf-8-sig", "utf-16", "latin-1"):
                        try:
                            with p.open('r', encoding=enc) as fh:
                                text = fh.read()
                            break
                        except UnicodeDecodeError:
                            continue
                    if text is None:
                        raise UnicodeDecodeError("All", b"", 0, 1, "Unable to decode file using common encodings")
                    if not text.strip():
                        logger.warning("Found service account file %s but it is empty", p)
                        continue
                    data = json.loads(text)
                except json.JSONDecodeError as jde:
                    logger.exception("Service account file %s exists but contains invalid JSON: %s", p, jde)
                    continue
                # Provide the parsed dict to credentials.Certificate so we guarantee the JSON validity
                cred = credentials.Certificate(data)
                firebase_admin.initialize_app(cred)
                logger.info("✅ Firebase initialized using %s", p)
                return firebase_admin
        except Exception:
            # Keep going on any exception to try other candidates
            logger.exception("Failed to initialize Firebase using %s", p)
            continue

    logger.warning(
        "Firebase was not initialized. No valid service account found. "
        "Set FIREBASE_SERVICE_ACCOUNT or FIREBASE_SERVICE_ACCOUNT_JSON to initialize the SDK."
    )
    return firebase_admin


# Do initialization on import so modules doing `from myproject.firebase import firebase_admin` can rely on the app
try:
    init_firebase()
except Exception:
    # Avoid raising on import; initialization issues will be logged and can be retried when needed
    logger.exception("Unexpected error when initializing Firebase Admin SDK on import")

__all__ = ["firebase_admin", "init_firebase"]
