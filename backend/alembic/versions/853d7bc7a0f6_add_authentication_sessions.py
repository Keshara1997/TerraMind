"""add authentication sessions

Revision ID: 853d7bc7a0f6
Revises: 115e13c0229e
Create Date: 2026-11-05 14:52:29.562506

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "853d7bc7a0f6"
down_revision: Union[str, None] = "115e13c0229e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("refresh_token_jti", sa.String(length=36), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_auth_sessions_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_auth_sessions")),
    )
    op.create_index(
        op.f("ix_auth_sessions_refresh_token_jti"),
        "auth_sessions",
        ["refresh_token_jti"],
        unique=True,
    )
    op.create_index(
        op.f("ix_auth_sessions_user_id"),
        "auth_sessions",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_auth_sessions_user_id"), table_name="auth_sessions")
    op.drop_index(
        op.f("ix_auth_sessions_refresh_token_jti"),
        table_name="auth_sessions",
    )
    op.drop_table("auth_sessions")




def upgrade() -> None:
    op.create_index(
        "ix_areas_geometry_gist",
        "areas",
        ["geometry"],
        unique=False,
        postgresql_using="gist",
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_areas_geometry_gist",
        table_name="areas",
    )