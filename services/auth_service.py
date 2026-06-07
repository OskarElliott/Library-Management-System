import bcrypt
from models.user import build_user

class AuthService:
    def __init__(self, connection):
        self.conn = connection

    def login(self, username, password):
        row = self.conn.execute(
            """
            SELECT u.user_id, u.username, u.email, u.password_hash,
                   u.is_active, r.role_name
            FROM Users u
            JOIN Roles r ON r.role_id = u.role_id
            WHERE u.username = ?
            """,
            (username,),
        ).fetchone()

        # return none for every failure to avoid leak which check failed
        if row is None:
            return None
        if not row["is_active"]:
            return None
        if not self._verify_password(password, row["password_hash"]):
            return None
        
        return build_user(row, row["role_name"])

    def _verify_password(self, password, stored_hash):
        return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
