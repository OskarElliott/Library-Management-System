from models.user import User

class Librarian(User):
    MAX_LOANS = 0
    MAX_LOAN_DAYS = 0

    def __init__(self, user_id, first_name, last_name, email, is_active, username):
        super().__init__(user_id, first_name, last_name, email, is_active)

        self._username = username

    @classmethod
    def from_row(cls, row):
        return cls(
            row["user_id"],
            row["first_name"],
            row["last_name"],
            row["email"],
            bool(row["is_active"]),
            row["username"],
        )