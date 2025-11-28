import os
import firebase_admin
from firebase_admin import credentials

cred_path = os.getenv("FIREBASE_KEY_PATH")  # Render secret path

try:
    if not firebase_admin._apps:
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print(f"✅ Firebase initialized at {cred_path}")
        else:
            raise FileNotFoundError(f"Firebase service account not found at {cred_path}")
except Exception as e:
    print(f"⚠️ Firebase initialization failed: {e}")
