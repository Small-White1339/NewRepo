"""为岗位和公开简历记录可核验来源。"""

from alembic import op
import sqlalchemy as sa

revision = "c71a9d2e4b80"
down_revision = "db7349f82947"
branch_labels = None
depends_on = None


def upgrade():
    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TYPE job_level ADD VALUE IF NOT EXISTS 'UNSPECIFIED'")
    for table in ["jobs", "resumes"]:
        op.add_column(table, sa.Column("source_name", sa.String(100), nullable=True))
        op.add_column(table, sa.Column("source_url", sa.String(1000), nullable=True))
        op.add_column(table, sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True))


def downgrade():
    for table in ["jobs", "resumes"]:
        op.drop_column(table, "imported_at")
        op.drop_column(table, "source_url")
        op.drop_column(table, "source_name")
