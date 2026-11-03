
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.auth_session import AuthSession
from app.models.user import User


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email.lower())
        return self.db.scalar(statement)

    def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.get(User, user_id)

    def create_user(
        self,
        email: str,
        full_name: str,
        hashed_password: str,
    ) -> User:
        user = User(
            email=email.lower(),
            full_name=full_name,
            hashed_password=hashed_password,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def create_session(
        self,
        user_id: uuid.UUID,
        token_jti: uuid.UUID,
        expires_at: datetime,
    ) -> AuthSession:
        session = AuthSession(
            user_id=user_id,
            refresh_token_jti=str(token_jti),
            expires_at=expires_at,
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    def get_active_session(
        self,
        token_jti: str,
    ) -> AuthSession | None:
        statement = select(AuthSession).where(
            AuthSession.refresh_token_jti == token_jti,
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > datetime.now(timezone.utc),
        )
        return self.db.scalar(statement)

    def revoke_session(self, session: AuthSession) -> None:
        session.revoked_at = datetime.now(timezone.utc)
        self.db.commit()
