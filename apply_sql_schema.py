"""
Load .env, connect to DATABASE_URL, and execute sql/web_schema.sql to create tables.

Usage:
    python apply_sql_schema.py
    # or inside docker container
    docker compose exec web python apply_sql_schema.py
"""

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


def main():
    base_dir = Path(__file__).resolve().parent
    sql_path = base_dir / "sql" / "web_schema.sql"

    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    load_dotenv(base_dir / ".env")
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL not set in environment or .env")

    sql = sql_path.read_text(encoding="utf-8")

    print(f"Connecting to database: {db_url}")
    with psycopg2.connect(db_url) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(sql)
    print("Schema applied successfully.")


if __name__ == "__main__":
    main()
