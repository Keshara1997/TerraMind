"""add capture workflow columns

Revision ID: a8f3c2d91e04
Revises: 04ecb971a73a
Create Date: 2026-11-18

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a8f3c2d91e04"
down_revision: Union[str, None] = "04ecb971a73a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _capture_columns(bind) -> set[str]:
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns("captures")}


def upgrade() -> None:
    bind = op.get_bind()
    existing = _capture_columns(bind)

    if "data_source_id" not in existing:
        op.add_column(
            "captures",
            sa.Column("data_source_id", sa.Uuid(), nullable=True),
        )
    if "created_by" not in existing:
        op.add_column(
            "captures",
            sa.Column("created_by", sa.Uuid(), nullable=True),
        )
    if "error_message" not in existing:
        op.add_column(
            "captures",
            sa.Column("error_message", sa.Text(), nullable=True),
        )

    inspector = sa.inspect(bind)
    fk_names = {fk["name"] for fk in inspector.get_foreign_keys("captures")}

    if op.f("fk_captures_data_source_id_data_sources") not in fk_names:
        op.create_foreign_key(
            op.f("fk_captures_data_source_id_data_sources"),
            "captures",
            "data_sources",
            ["data_source_id"],
            ["id"],
            ondelete="SET NULL",
        )

    if op.f("fk_captures_created_by_users") not in fk_names:
        op.create_foreign_key(
            op.f("fk_captures_created_by_users"),
            "captures",
            "users",
            ["created_by"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_captures_created_by_users"),
        "captures",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_captures_data_source_id_data_sources"),
        "captures",
        type_="foreignkey",
    )
    op.drop_column("captures", "error_message")
    op.drop_column("captures", "created_by")
    op.drop_column("captures", "data_source_id")