from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from firebase_admin import auth

from .firebase import initialize_firebase


security = HTTPBearer(
    auto_error=False
)


def get_current_user(
    credentials: Optional[
        HTTPAuthorizationCredentials
    ] = Depends(security)
):

    initialize_firebase()

    # -----------------------------------------
    # Guest request
    # -----------------------------------------

    if credentials is None:
        return None


    # -----------------------------------------
    # Authenticated request
    # -----------------------------------------

    token = credentials.credentials

    try:

        decoded_token = auth.verify_id_token(
            token
        )

        return decoded_token

    except Exception as exc:

        print(
            "[AUTH ERROR]",
            repr(exc)
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token."
        )