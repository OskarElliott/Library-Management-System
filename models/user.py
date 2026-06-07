from abc import ABC, abstractmethod

class User(ABC): # superclass
    def __init__(self, user_id, username, email, role_name):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role_name = role_name

    @abstractmethod # polymorphism
    def max_loan_days(self):
        ...

    @abstractmethod
    def max_loans(self):
        ...

    # eligibility numbers come from borrowing_eligibility view
    def can_borrow(self, outstanding_fines, active_loans):
        return outstanding_fines == 0 and active_loans < self.max_loans()

class Student(User):
    def max_loan_days(self):
        return 14
    
    def max_loans(self):
        return 3

class Teacher(User):
    def max_loan_days(self):
        return 60
    
    def max_loans(self):
        return 8
    
class Librarian(User):
    def max_loan_days(self):
        return 60
    
    def max_loans(self):
        return 8
    
def build_user(row, role_name):
    user_classes = {
        "student" : Student,
        "teacher" : Teacher,
        "librarian" : Librarian,
    }
    cls = user_classes.get(role_name.lower())
    if cls is None:
        raise ValueError(f"unknown role: {role_name}")
    return cls(row["user_id"], row["username"], row["email"], role_name)