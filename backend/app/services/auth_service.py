
import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.jwt import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.core.security import hash_password, verify_password
from app.repositories.auth_repository import AuthRepository
from app.schemas.auth import UserLogin, UserRegister


class AuthService:
    def __init__(self, db: Session):
        self.repository = AuthRepository(db)

    def register(self, data: UserRegister):
        email = str(data.email).lower()

        if self.repository.get_user_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            )

        hashed_password = hash_password(data.password)

        try:
            user = self.repository.create_user(
                email=email,
                full_name=data.full_name.strip(),
                hashed_password=hashed_password,
            )
        except IntegrityError:
            self.repository.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            )

        return user

    def login(self, data: UserLogin) -> dict:
        email = str(data.email).lower()
        user = self.repository.get_user_by_email(email)

        if (
            user is None
            or not user.is_active
            or not verify_password(data.password, user.hashed_password)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token, expires_in = create_access_token(user.id)

        refresh_token, token_jti, expires_at = create_refresh_token(
            user.id
        )

        self.repository.create_session(
            user_id=user.id,
            token_jti=token_jti,
            expires_at=expires_at,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": expires_in,
        }

    def refresh(self, token: str) -> dict:
        from jwt import InvalidTokenError

        try:
            payload = decode_refresh_token(token)
            user_id = uuid.UUID(payload["sub"])
            token_jti = payload["jti"]
        except (InvalidTokenError, ValueError, KeyError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        session = self.repository.get_active_session(token_jti)

        if session is None or session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh session is invalid or revoked",
            )

        user = self.repository.get_user_by_id(user_id)

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is unavailable",
            )

        # Rotate refresh token: revoke the old session first.
        self.repository.revoke_session(session)

        access_token, expires_in = create_access_token(user.id)
        refresh_token, new_jti, expires_at = create_refresh_token(user.id)

        self.repository.create_session(
            user_id=user.id,
            token_jti=new_jti,
            expires_at=expires_at,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": expires_in,
        }

    def logout(self, token: str) -> None:
        from jwt import InvalidTokenError

        try:
            payload = decode_refresh_token(token)
            token_jti = payload["jti"]
        except (InvalidTokenError, KeyError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        session = self.repository.get_active_session(token_jti)

        if session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh session is invalid or already revoked",
            )

        self.repository.revoke_session(session)
