
"""ensure area geometry spatial index

Revision ID: 2c056bc1b63c
Revises: 853d7bc7a0f6
Create Date: 2026-11-05 16:48:13.246726

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



revision: str = '2c056bc1b63c'
down_revision: Union[str, None] = '853d7bc7a0f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


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
        if_exists=True,
    )
