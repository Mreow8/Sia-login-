"""
myproject package initializer.
We import the firebase module so the Firebase Admin SDK is initialized early on at Django startup.
"""
from . import firebase as _firebase  # noqa: F401 - initialize on import

# re-export the initializer for convenience
init_firebase = _firebase.init_firebase

