import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "library.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

def get_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path) # foreign keys are off by default in sqltie so it has to be set per connection
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=DB_PATH):
    schema = SCHEMA_PATH.read_text()
    conn = get_connection(db_path)
    conn.executescript(schema)
    conn.commit()
    conn.close()
