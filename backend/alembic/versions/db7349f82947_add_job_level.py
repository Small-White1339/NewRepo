"""add_job_level

Revision ID: db7349f82947
Revises: e7d1808793e6
Create Date: 2026-07-15 17:05:12.477081
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db7349f82947'
down_revision: Union[str, None] = 'e7d1808793e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL 新增列前需要先创建枚举；默认值兼容已有岗位记录。
    job_level = sa.Enum('JUNIOR', 'INTERMEDIATE', 'SENIOR', 'EXPERT', name='job_level')
    if op.get_bind().dialect.name == 'postgresql':
        job_level.create(op.get_bind(), checkfirst=True)
    op.add_column('jobs', sa.Column('level', job_level, nullable=False, server_default='INTERMEDIATE'))


def downgrade() -> None:
    op.drop_column('jobs', 'level')
    if op.get_bind().dialect.name == 'postgresql':
        sa.Enum(name='job_level').drop(op.get_bind(), checkfirst=True)
