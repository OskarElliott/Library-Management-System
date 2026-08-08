class User:
    MAX_LOANS = None
    MAX_LOAN_DAYS = None

    def __init__(self, user_id, first_name, last_name, email, is_active):
        if type(self) is User: # prevents creation of a generic user, only subclasses can exist
            raise TypeError("User is an abstract class")

        self._user_id = user_id
        self._first_name = first_name
        self._last_name = last_name
        self._email = email
        self._is_active = is_active

    def __str__(self):
        return f"{self._first_name} {self._last_name} ({self._email})"

    @classmethod
    def from_row(cls, row):
        return cls(
            row["user_id"],
            row["first_name"],
            row["last_name"],
            row["email"],
            bool(row["is_active"])
        )

    def get_first_name(self):
        return self._first_name

    def get_last_name(self):
        return self._last_name