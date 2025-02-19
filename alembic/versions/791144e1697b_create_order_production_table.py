"""create order production table

Revision ID: 791144e1697b
Revises:
Create Date: 2025-02-19 15:58:02.690799

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '791144e1697b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'order',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('external_id', sa.String(length=120), nullable=False),
        sa.Column('status', sa.String(length=60), nullable=False),
        sa.Column('items', JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_customer')),
        sa.UniqueConstraint('external_id', name=op.f('uq_external_id'))
    )


def downgrade() -> None:
    op.drop_table('order')
