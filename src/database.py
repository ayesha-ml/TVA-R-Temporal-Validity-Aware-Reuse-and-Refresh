from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "database" / "research.db"
SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema.sql"


def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with get_connection() as connection:
        connection.executescript(schema)
        connection.commit()


def list_tables():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()

    return [row[0] for row in rows]


if __name__ == "__main__":
    initialize_database()
    print("database tables:", list_tables())\n