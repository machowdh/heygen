from typing import Annotated
from fastapi import Security, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from app.db import is_valid, get_user

api_key_header = APIKeyHeader(name="X-Api-Key")


def get_current_user(api_key_header: str = Security(api_key_header)) -> str:
    """
    Dependency to validate the API key and retrieve the current user.
    """
    if is_valid(api_key_header):
        return get_user(api_key_header)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid API key"
    )


CurrentUserDep = Annotated[str, Depends(get_current_user)]
