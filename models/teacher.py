from models.user import User

class Teacher(User):
    MAX_LOANS = 10
    MAX_LOAN_DAYS = 30

