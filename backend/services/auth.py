from datetime import datetime, timedelta, timezone
import os

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from uuid import UUID
import jwt

from models import storage
from models.session import UserSession
from models.user import User
from schemas.auth import AuthSchema

load_dotenv()

SECRET_KEY = os.environ["USER_SECRET_KEY"]
JWT_ALGORITHM = os.environ["JWT_ALGORITHM"]
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.environ["ACCESS_TOKEN_EXPIRE_SECONDS"])
SESSION_EXPIRE_DAYS = int(os.environ["SESSION_EXPIRE_DAYS"])


def datetime_now_utc(days: int = 0, seconds: int = 0):
    return datetime.now(timezone.utc) + timedelta(days=days, seconds=seconds)


def O2AuthSchemaAccess(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Access token missing.")
    try:
        token_type, token_value = token.split(" ")
        if token_type.lower() == "bearer":
            return token_value
        raise HTTPException(status_code=401, detail="Invalid token type.")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token format.")


def O2AuthSchemaRefresh(request: Request):
    token = request.cookies.get("refresh_token")
    if token:
        try:
            token_type, token_value = token.split(" ")
            if token_type.lower() == "bearer":
                return token_value
            raise HTTPException(status_code=401, detail="Invalid token type.")
        except ValueError:
            raise HTTPException(
                status_code=401, detail="Invalid token format.")
    raise HTTPException(status_code=401, detail="Refresh token missing.")


def create_access_token(session_id: str | UUID, user_id: str | UUID):
    return jwt.encode({
        "session_id": str(session_id),
        "user_id": str(user_id),
        "exp": datetime_now_utc(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
    }, SECRET_KEY, JWT_ALGORITHM)


def create_refresh_token(session_id: str | UUID, user_id: str | UUID):
    return jwt.encode({
        "session_id": str(session_id),
        "user_id": str(user_id),
        "exp": datetime_now_utc(days=SESSION_EXPIRE_DAYS)
    }, SECRET_KEY, JWT_ALGORITHM)


def generate_tokens(response: JSONResponse, user: User, user_session: UserSession = None):
    if not user_session:
        user_session = UserSession(user_id=user.id)
        storage.new(user_session)
        storage.save()

    access_token = create_access_token(user_session.id, user.id)
    refresh_token = create_refresh_token(user_session.id, user.id)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token", "/auth/")
    response.set_cookie(
        key="access_token",
        value=f"bearer {access_token}",
        max_age=ACCESS_TOKEN_EXPIRE_SECONDS,
        httponly=True,
        path="/",
        samesite="lax",
        secure=False,
    )
    response.set_cookie(
        key="refresh_token",
        value=f"bearer {refresh_token}",
        max_age=SESSION_EXPIRE_DAYS * 24 * 3600,
        httponly=True,
        path="/auth/",
        samesite="lax",
        secure=False,
    )
    return response


def login_service(user_data: AuthSchema):
    email = user_data.email.lower().strip()
    user = storage.get("user", email=email)

    if not (user and user.checkpw(user_data.password)):
        raise HTTPException(
            status_code=401, detail="Invalid email or password.")

    response = JSONResponse(
        {"detail": "User loggged in successfully!", "user": user.to_dict()})
    return generate_tokens(response, user)


def verify_user(token: str = Depends(O2AuthSchemaAccess)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        session_id = payload.get("session_id")
        user_id = payload.get("user_id")
        exp = payload.get("exp")

        if not (session_id and user_id and exp):
            raise HTTPException(
                status_code=401, detail="Invalid token payload.")

        session = storage.get("session", id=session_id)
        if not session or session.expire_at < datetime_now_utc():
            raise HTTPException(
                status_code=401, detail="Session expired or invalid.")

        user = storage.get("user", id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=401, detail="Invalid token signature.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")


def refresh_tokens_service(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY,
                             algorithms=[JWT_ALGORITHM])
        session_id = payload.get("session_id")
        user_id = payload.get("user_id")
        exp = payload.get("exp")

        if not (session_id and user_id and exp):
            raise HTTPException(
                status_code=401, detail="Invalid refresh token payload.")

        session = storage.get("session", id=session_id)
        if not session or session.expire_at < datetime_now_utc():
            raise HTTPException(
                status_code=401, detail="Session expired or invalid.")

        user = storage.get("user", id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        session.expire_at = datetime_now_utc(days=SESSION_EXPIRE_DAYS)
        storage.new(session)
        storage.save()

        response = JSONResponse({"detail": "Tokens refreshed successfully."})
        return generate_tokens(response, user, session)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401, detail="Refresh token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token.")


def logout_service(refresh_token: str):

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY,
                             algorithms=[JWT_ALGORITHM])
        session_id = payload.get("session_id")

        session = storage.get("session", id=session_id)
        if session_id and session:
            storage.delete(session)
            storage.save()
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        pass
    response = JSONResponse({"detail": "Logged out successfully."})

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token", "/auth/")
    return response
