from models.user import User

class Student(User):
    MAX_LOANS = 3
    MAX_LOAN_DAYS = 14

    def __init__(self, user_id, first_name, last_name, email, is_active, homeroom, year_number):
        super().__init__(user_id, first_name, last_name, email, is_active)
    
        self._homeroom = homeroom
        self._year_number = year_number
    
    @classmethod
    def from_row(cls, row):
        return cls(
            row["user_id"],
            row["first_name"],
            row["last_name"],
            row["email"],
            bool(row["is_active"]),
            row["homeroom"],
            row["year_number"],
        )