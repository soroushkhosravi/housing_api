"""create new file

Revision ID: 23d2f57a58c1
Revises: 
Create Date: 2022-10-18 16:33:04.057611

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23d2f57a58c1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute("""CREATE TABLE users (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          email TEXT UNIQUE NOT NULL,
          profile_pic TEXT NOT NULL
        );"""
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute("DROP TABLE users")
