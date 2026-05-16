"""split event datetime into date time_start time_end

Revision ID: 999afccfcd7b
Revises: 09208680f46a
Create Date: 2026-04-19 20:04:10.541329

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '999afccfcd7b'
down_revision: Union[str, Sequence[str], None] = '09208680f46a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('events', sa.Column('date', sa.Date(), nullable=True))
    op.add_column('events', sa.Column('time_start', sa.Time(), nullable=True))
    op.add_column('events', sa.Column('time_end', sa.Time(), nullable=True))

    op.execute("UPDATE events SET date = start::date, time_start = start::time, time_end = \"end\"::time")

    op.alter_column('events', 'date', nullable=False)
    op.alter_column('events', 'time_start', nullable=False)
    op.alter_column('events', 'time_end', nullable=False)

    op.drop_column('events', 'start')
    op.drop_column('events', 'end')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('events', sa.Column('start', sa.DateTime(), nullable=True))
    op.add_column('events', sa.Column('end', sa.DateTime(), nullable=True))

    op.execute('UPDATE events SET start = (date + time_start)::timestamp, "end" = (date + time_end)::timestamp')

    op.alter_column('events', 'start', nullable=False)
    op.alter_column('events', 'end', nullable=False)

    op.drop_column('events', 'date')
    op.drop_column('events', 'time_start')
    op.drop_column('events', 'time_end')
