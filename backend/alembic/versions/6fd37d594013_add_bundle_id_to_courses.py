"""Add bundle_id to courses

Revision ID: 6fd37d594013
Revises: f84add151dda
Create Date: 2026-03-11 22:10:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6fd37d594013"
down_revision: Union[str, None] = "f84add151dda"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("courses", sa.Column("bundle_id", sa.String(length=50), nullable=True))
    op.create_index(op.f("ix_courses_bundle_id"), "courses", ["bundle_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_courses_bundle_id"), table_name="courses")
    op.drop_column("courses", "bundle_id")
