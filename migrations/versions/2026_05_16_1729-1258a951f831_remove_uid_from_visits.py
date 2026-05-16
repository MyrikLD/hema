"""remove uid from visits

Revision ID: 1258a951f831
Revises: 8f6400caec9b
Create Date: 2026-05-16 17:29:45.901008

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1258a951f831'
down_revision: Union[str, Sequence[str], None] = '8f6400caec9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint('visits_pkey', 'visits', type_='primary')
    op.drop_column('visits', 'uid')
    op.execute("ALTER TABLE visits ADD COLUMN id SERIAL PRIMARY KEY")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('visits_pkey', 'visits', type_='primary')
    op.drop_column('visits', 'id')
    op.add_column('visits', sa.Column('uid', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.execute("UPDATE visits SET uid = timestamp::text")
    op.create_primary_key('visits_pkey', 'visits', ['timestamp', 'uid'])
