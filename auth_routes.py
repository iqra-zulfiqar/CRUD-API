from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, field_validator

from supabase_client import supabase
from auth_dependency import get_current_user

router = APIRouter()


class AuthCredentials(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("email must not be empty")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_must_not_be_blank(cls, v: str) -> str:
        if not v:
            raise ValueError("password must not be empty")
        return v


@router.post(
    "/auth/signup",
    status_code=201,
    tags=["auth"],
    summary="Create a new account",
)
def signup(payload: AuthCredentials):
    try:
        result = supabase.auth.sign_up(
            {"email": payload.email, "password": payload.password}
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if result.user is None:
        raise HTTPException(status_code=400, detail="Signup failed")

    return {
        "id": result.user.id,
        "email": result.user.email,
        "created_at": str(result.user.created_at),
    }


@router.post(
    "/auth/login",
    tags=["auth"],
    summary="Log in and receive a JWT",
)
def login(payload: AuthCredentials):
    try:
        result = supabase.auth.sign_in_with_password(
            {"email": payload.email, "password": payload.password}
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login credentials")

    if result.session is None:
        raise HTTPException(status_code=401, detail="Invalid login credentials")

    return {
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token,
        "token_type": "bearer",
    }


@router.post(
    "/auth/logout",
    status_code=204,
    tags=["auth"],
    summary="Log out (requires a valid token)",
)
def logout(current=Depends(get_current_user)):
    user, token = current
    try:
        supabase.auth.sign_out()
    except Exception:
        # Sign-out failing server-side shouldn't block the client from
        # discarding its token locally; the important security property
        # (the token was verified before this ran) already held.
        pass
    return None