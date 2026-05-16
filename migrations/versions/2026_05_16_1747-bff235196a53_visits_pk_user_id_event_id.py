"""visits pk user_id event_id

Revision ID: bff235196a53
Revises: 1258a951f831
Create Date: 2026-05-16 17:47:19.857588

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bff235196a53'
down_revision: Union[str, Sequence[str], None] = '1258a951f831'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('visits', 'user_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('visits', 'event_id', existing_type=sa.INTEGER(), nullable=False)
    op.drop_constraint(op.f('visits_user_id_event_id_key'), 'visits', type_='unique')
    op.drop_constraint(op.f('visits_event_id_fkey'), 'visits', type_='foreignkey')
    op.drop_constraint(op.f('visits_user_id_fkey'), 'visits', type_='foreignkey')
    op.drop_constraint('visits_pkey', 'visits', type_='primary')
    op.drop_column('visits', 'id')
    op.create_primary_key('visits_pkey', 'visits', ['user_id', 'event_id'])
    op.create_foreign_key(op.f('visits_user_id_fkey'), 'visits', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(op.f('visits_event_id_fkey'), 'visits', 'events', ['event_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f('visits_user_id_fkey'), 'visits', type_='foreignkey')
    op.drop_constraint(op.f('visits_event_id_fkey'), 'visits', type_='foreignkey')
    op.drop_constraint('visits_pkey', 'visits', type_='primary')
    op.execute("ALTER TABLE visits ADD COLUMN id SERIAL PRIMARY KEY")
    op.create_foreign_key(op.f('visits_user_id_fkey'), 'visits', 'users', ['user_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(op.f('visits_event_id_fkey'), 'visits', 'events', ['event_id'], ['id'], ondelete='SET NULL')
    op.create_unique_constraint(op.f('visits_user_id_event_id_key'), 'visits', ['user_id', 'event_id'])
    op.alter_column('visits', 'event_id', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('visits', 'user_id', existing_type=sa.INTEGER(), nullable=True)
