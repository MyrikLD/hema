"""split weekly_event datetime into weekday time_start time_end

Revision ID: 8a309355cec7
Revises: 999afccfcd7b
Create Date: 2026-04-19 20:10:50.876496

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8a309355cec7"
down_revision: Union[str, Sequence[str], None] = "999afccfcd7b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("weekly_events", sa.Column("weekday", sa.SmallInteger(), nullable=True))
    op.add_column("weekly_events", sa.Column("time_start", sa.Time(), nullable=True))
    op.add_column("weekly_events", sa.Column("time_end", sa.Time(), nullable=True))

    # PostgreSQL EXTRACT(DOW): 0=Sunday … 6=Saturday
    # Python weekday(): 0=Monday … 6=Sunday  →  (DOW + 6) % 7
    op.execute("""
        UPDATE weekly_events SET
            weekday    = ((EXTRACT(DOW FROM event_start)::int + 6) % 7)::smallint,
            time_start = event_start::time,
            time_end   = event_end::time
    """)

    op.alter_column("weekly_events", "weekday", nullable=False)
    op.alter_column("weekly_events", "time_start", nullable=False)
    op.alter_column("weekly_events", "time_end", nullable=False)

    op.drop_column("weekly_events", "event_start")
    op.drop_column("weekly_events", "event_end")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column("weekly_events", sa.Column("event_start", sa.DateTime(), nullable=True))
    op.add_column("weekly_events", sa.Column("event_end", sa.DateTime(), nullable=True))

    # Reconstruct using 2024-01-01 (Monday) + weekday days as reference date
    op.execute("""
        UPDATE weekly_events SET
            event_start = ('2024-01-01'::date + weekday) + time_start,
            event_end   = ('2024-01-01'::date + weekday) + time_end
    """)

    op.alter_column("weekly_events", "event_start", nullable=False)
    op.alter_column("weekly_events", "event_end", nullable=False)

    op.drop_column("weekly_events", "weekday")
    op.drop_column("weekly_events", "time_start")
    op.drop_column("weekly_events", "time_end")
