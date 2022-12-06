"""create new file

Revision ID: 23d2f57a58c1
Revises: 
Create Date: 2022-10-18 16:33:04.057611

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '23d2f57a58c1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('google_id', sa.String, nullable=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('email', sa.String, nullable=False),
        sa.Column('profile_pic', sa.Unicode(200)),
    )
    op.create_index('google_id_index', 'users', ['google_id'])

def downgrade() -> None:
    op.drop_table('users')
