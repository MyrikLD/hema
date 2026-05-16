"""enforce not null on weekly_events columns

Revision ID: e20434a4db5e
Revises: 8a309355cec7
Create Date: 2026-04-19 20:18:51.911240

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e20434a4db5e'
down_revision: Union[str, Sequence[str], None] = '8a309355cec7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Fill any NULLs before enforcing NOT NULL
    op.execute("UPDATE weekly_events SET name = '' WHERE name IS NULL")
    op.execute("UPDATE weekly_events SET start = CURRENT_DATE WHERE start IS NULL")
    op.execute('UPDATE weekly_events SET "end" = CURRENT_DATE WHERE "end" IS NULL')

    op.alter_column('weekly_events', 'name', nullable=False)
    op.alter_column('weekly_events', 'start', nullable=False)
    op.alter_column('weekly_events', 'end', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('weekly_events', 'name', nullable=True)
    op.alter_column('weekly_events', 'start', nullable=True)
    op.alter_column('weekly_events', 'end', nullable=True)
