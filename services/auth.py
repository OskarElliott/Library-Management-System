import bcrypt

from db.connection import get_connection
from models.librarian import Librarian

def login(username, password):
    con = get_connection()

    try:
        cur = con.cursor()
        cur.execute("""SELECT Users.user_id, Users.first_name, Users.last_name, Users.email, Users.is_active, Users.username, Users.password_hash
                    FROM Users JOIN Roles ON Users.role_id = Roles.role_id WHERE username = ? AND Users.is_active = 1 AND Roles.role_name = 'librarian'""", (username,))
        row = cur.fetchone()

    finally:
        con.close()

    # return the same result for an unknown username and an incorrect password to avoid revealing which usernames exist
    if row is None:
        return None

    # the password hash is stored as text, so both values must be encoded to bytes
    if not bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
        return None

    return Librarian.from_row(row)