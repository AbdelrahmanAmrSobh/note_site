from fastapi import APIRouter, Depends

from schemas.auth import AuthSchema
from services.auth import login_service, logout_service, O2AuthSchemaRefresh, refresh_tokens_service

router = APIRouter(prefix="/auth")


@router.post("/login", status_code=200)
def login(user: AuthSchema):
    return login_service(user)


@router.get("/logout", status_code=200)
def logout(refresh_token: str = Depends(O2AuthSchemaRefresh)):
    return logout_service(refresh_token)


@router.post("/refresh-tokens", status_code=200)
def refresh_tokens(refresh_token: str = Depends(O2AuthSchemaRefresh)):
    return refresh_tokens_service(refresh_token)
