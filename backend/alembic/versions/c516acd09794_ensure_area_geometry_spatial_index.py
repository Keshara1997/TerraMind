
"""ensure area geometry spatial index

Revision ID: c516acd09794
Revises: 2c056bc1b63c
Create Date: 2026-11-07 09:43:09.027937

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



revision: str = 'c516acd09794'
down_revision: Union[str, None] = '2c056bc1b63c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
