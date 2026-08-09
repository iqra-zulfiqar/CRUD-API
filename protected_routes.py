from fastapi import APIRouter, Depends

from auth_dependency import get_current_user

router = APIRouter()


@router.get("/public/info", tags=["public"], summary="Public info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@router.get("/protected/profile", tags=["protected"], summary="Get your profile")
def profile(current=Depends(get_current_user)):
    user, _token = current
    return {
        "id": user.id,
        "email": user.email,
        "created_at": str(user.created_at),
    }


@router.get(
    "/protected/dashboard",
    tags=["protected"],
    summary="Protected dashboard (demonstrates the middleware on a 2nd route)",
)
def dashboard(current=Depends(get_current_user)):
    user, _token = current
    return {"message": f"Welcome to your dashboard, {user.email}!"}