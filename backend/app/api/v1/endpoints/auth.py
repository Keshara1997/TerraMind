
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import (
    AccessTokenResponse,
    UserLogin,
    UserRead,
    UserRegister,
)
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Authentication"])

REFRESH_COOKIE_NAME = "aleph_refresh_token"


def set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.APP_ENV.lower() == "production",
        samesite="lax",
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/v1/auth",
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        httponly=True,
        secure=settings.APP_ENV.lower() == "production",
        samesite="lax",
        path="/api/v1/auth",
    )


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: UserRegister,
    db: Session = Depends(get_db),
):
    return AuthService(db).register(data)


@router.post("/login", response_model=AccessTokenResponse)
def login(
    data: UserLogin,
    response: Response,
    db: Session = Depends(get_db),
):
    tokens = AuthService(db).login(data)

    set_refresh_cookie(response, tokens["refresh_token"])

    return {
        "access_token": tokens["access_token"],
        "token_type": "bearer",
        "expires_in": tokens["expires_in"],
    }


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(
        default=None,
        alias=REFRESH_COOKIE_NAME,
    ),
    db: Session = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token cookie is missing",
        )

    tokens = AuthService(db).refresh(refresh_token)

    set_refresh_cookie(response, tokens["refresh_token"])

    return {
        "access_token": tokens["access_token"],
        "token_type": "bearer",
        "expires_in": tokens["expires_in"],
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    refresh_token: str | None = Cookie(
        default=None,
        alias=REFRESH_COOKIE_NAME,
    ),
    db: Session = Depends(get_db),
):
    if refresh_token:
        AuthService(db).logout(refresh_token)

    clear_refresh_cookie(response)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={
            "Set-Cookie": (
                f"{REFRESH_COOKIE_NAME}=; Max-Age=0; Path=/api/v1/auth; "
                "HttpOnly; SameSite=Lax"
            )
        },
    )


@router.get("/me", response_model=UserRead)
def get_me(
    current_user: User = Depends(get_current_active_user),
):
    return current_user
