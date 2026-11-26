from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
def me(user: CurrentUser = Depends(get_current_user)) -> dict:
    """Who the backend thinks you are. Proves the browser's Supabase login is accepted here."""
    return {"id": user.id, "email": user.email}
