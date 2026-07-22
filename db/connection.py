from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parent.parent / "library.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

def get_connection():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON") # foreign keys off by default
    return con

def init_db():
    schema_text = SCHEMA_PATH.read_text(encoding="utf-8") # for windows/mac code compatibility (windows defaults to non utf-8 encoding)
    con = get_connection()
    con.executescript(schema_text)
    con.commit()
    con.close()