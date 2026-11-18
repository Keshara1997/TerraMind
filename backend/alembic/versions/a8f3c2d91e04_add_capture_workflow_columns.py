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


def upgrade() -> None:
    op.add_column(
        "captures",
        sa.Column("data_source_id", sa.Uuid(), nullable=True),
    )
    op.add_column(
        "captures",
        sa.Column("created_by", sa.Uuid(), nullable=True),
    )
    op.add_column(
        "captures",
        sa.Column("error_message", sa.Text(), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_captures_data_source_id_data_sources"),
        "captures",
        "data_sources",
        ["data_source_id"],
        ["id"],
        ondelete="SET NULL",
    )
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