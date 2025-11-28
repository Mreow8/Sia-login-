import os
import json
import firebase_admin
from firebase_admin import credentials

# Check for Render environment variable first
firebase_json_str = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')

if not firebase_admin._apps:
    if firebase_json_str:
        try:
            # Load JSON from environment variable
            cred_dict = json.loads(firebase_json_str)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized from environment variable")
        except Exception as e:
            print(f"⚠️ Firebase initialization failed: {e}")
    else:
        # Fallback to local file (Windows dev)
        local_path = r"C:\sia-projec\firebase\serviceAccountKey.json"
        if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
            try:
                cred = credentials.Certificate(local_path)
                firebase_admin.initialize_app(cred)
                print(f"✅ Firebase initialized from local file: {local_path}")
            except Exception as e:
                print(f"⚠️ Firebase initialization failed from local file: {e}")
        else:
            print(f"⚠️ Firebase credentials not found or empty at {local_path}")
