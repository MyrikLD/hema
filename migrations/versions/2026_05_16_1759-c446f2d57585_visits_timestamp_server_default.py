"""visits timestamp server default

Revision ID: c446f2d57585
Revises: bff235196a53
Create Date: 2026-05-16 17:59:27.905947

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c446f2d57585'
down_revision: Union[str, Sequence[str], None] = 'bff235196a53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('visits', 'timestamp', server_default=sa.text("now()"))


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('visits', 'timestamp', server_default=None)
