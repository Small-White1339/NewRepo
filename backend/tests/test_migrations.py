"""验证已有数据的数据库升级和回退。"""

import sqlite3

from alembic import command
from alembic.config import Config

from app.config import settings


def test_upgrade_existing_jobs_and_downgrade(tmp_path, monkeypatch):
    database = tmp_path / "migration.db"
    monkeypatch.setattr(settings, "DATABASE_URL", f"sqlite+aiosqlite:///{database}")
    config = Config("alembic.ini")
    command.upgrade(config, "e7d1808793e6")
    with sqlite3.connect(database) as connection:
        connection.execute("""
            INSERT INTO users (id, username, email, hashed_password, role, is_active)
            VALUES ('00000000000000000000000000000001', 'legacy', 'legacy@example.com', 'hash', 'HR', 1)
        """)
        connection.execute("""
            INSERT INTO jobs (id, user_id, title, company, status)
            VALUES ('00000000000000000000000000000002', '00000000000000000000000000000001', 'Legacy job', 'Test', 'ACTIVE')
        """)
    command.upgrade(config, "head")
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT level FROM jobs").fetchone()[0] == "INTERMEDIATE"
    command.downgrade(config, "e7d1808793e6")
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT title FROM jobs").fetchone()[0] == "Legacy job"
