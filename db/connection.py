from pathlib import Path
import sqlite3

# build the path relative to this file so it works from any working directory
DB_PATH = Path(__file__).resolve().parent.parent / "library.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

def get_connection():
    con = sqlite3.connect(DB_PATH)
    # return rows that can be accessed by column name instead of only by index
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON") # foreign keys off by default
    return con

def init_db():
    schema_text = SCHEMA_PATH.read_text(encoding="utf-8") # windows doesn't default to utf-8
    con = get_connection()
    con.executescript(schema_text)
    con.commit()
    con.close()