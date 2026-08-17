import json
import os

import firebase_admin
from firebase_admin import credentials


def initialize_firebase():

    if firebase_admin._apps:
        return firebase_admin.get_app()

    # ==========================================
    # Production: Environment Variable
    # ==========================================

    service_account_json = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_JSON"
    )

    if service_account_json:

        try:

            service_account_info = json.loads(
                service_account_json
            )

        except json.JSONDecodeError as exc:

            raise RuntimeError(
                "FIREBASE_SERVICE_ACCOUNT_JSON "
                "contains invalid JSON."
            ) from exc

        cred = credentials.Certificate(
            service_account_info
        )

        return firebase_admin.initialize_app(
            cred
        )

    # ==========================================
    # Local Development: JSON File
    # ==========================================

    service_account_path = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_PATH",
        "firebase-service-account.json"
    )

    if os.path.exists(service_account_path):

        cred = credentials.Certificate(
            service_account_path
        )

        return firebase_admin.initialize_app(
            cred
        )

    # ==========================================
    # No Credentials
    # ==========================================

    raise RuntimeError(
        "Firebase Admin credentials not configured. "
        "Set FIREBASE_SERVICE_ACCOUNT_JSON or "
        "FIREBASE_SERVICE_ACCOUNT_PATH."
    )


initialize_firebase()