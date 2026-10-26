from db.connection import get_connection
from services import users, fines
from datetime import date, timedelta

ACTION_ISSUE_LOAN = "issue_loan"
ACTION_RETURN_LOAN = "return_loan"
ACTION_MARK_LOST = "mark_lost"

def get_active_loans(today):
    con = get_connection()
    try:
        cur = con.cursor()

        cur.execute("""SELECT Loans.loan_id, Users.first_name, Users.last_name, Books.title, Loans.copy_id, Loans.checkout_date, Loans.due_date, julianday(Loans.due_date) - julianday(?) AS days_remaining
                FROM Loans JOIN BookCopies ON Loans.copy_id = BookCopies.copy_id JOIN Books ON BookCopies.book_id = Books.book_id
                JOIN Users ON Loans.user_id = Users.user_id
                WHERE Loans.status = 'active' ORDER BY Loans.due_date ASC""", (today,))

        rows = cur.fetchall()
    finally:
        con.close()

    return rows

def get_overdue_loans(today):
    con = get_connection()
    try:
        cur = con.cursor()

        # strict < so a loan due today isn't overdue
        cur.execute("""SELECT Loans.loan_id, Users.first_name, Users.last_name, Books.title, Loans.copy_id, Loans.checkout_date, Loans.due_date, julianday(?) - julianday(Loans.due_date) AS days_overdue
                    FROM Loans JOIN BookCopies ON Loans.copy_id = BookCopies.copy_id JOIN Books ON BookCopies.book_id = Books.book_id
                    JOIN Users ON Loans.user_id = Users.user_id
                    WHERE Loans.status = 'active' AND Loans.due_date < ? ORDER BY days_overdue DESC""", (today, today))

        rows = cur.fetchall()
    finally:
        con.close()

    return rows

def check_eligibility(user_id):
    user = users.get_user(user_id)

    con = get_connection()

    try:
        cur = con.cursor()
        cur.execute("SELECT active_loans, outstanding_fines FROM BorrowingEligibility WHERE user_id = ?", (user_id,))
        row = cur.fetchone()

    finally:
        con.close()

    # collects all issues so the user sees everything at once
    reasons = []

    if not user.get_is_active():
        reasons.append("Account is inactive.")

    if row["active_loans"] >= user.MAX_LOANS:
        reasons.append(f"Borrower has reached the loan limit ({row['active_loans']} of {user.MAX_LOANS} loans).")

    if row["outstanding_fines"] > 0:
        reasons.append(f"Borrower has outstanding fines of {row['outstanding_fines']:.2f} PLN.")

    return reasons
def issue_loan(copy_id, user_id, librarian_id, today):
    # the dialog checks eligibility when a borrower is selected, but the service checks again when issuing the loan so other callers cannot bypass the rules
    reasons = check_eligibility(user_id)

    if reasons:
        raise ValueError("\n".join(reasons))

    con = get_connection()
    
    try:
        cur = con.cursor()

        cur.execute("SELECT status FROM BookCopies WHERE copy_id = ?", (copy_id,))

        row = cur.fetchone()

        if row is None:
            raise ValueError("Copy not found.")

        if row["status"] != "available":
            raise ValueError("Copy is unavailable.")

        user = users.get_user(user_id)
        due_date = date.fromisoformat(today) + timedelta(days=user.MAX_LOAN_DAYS)

        with con:
            cur.execute("""INSERT INTO Loans(copy_id, user_id, checkout_date, due_date, status)
                        VALUES (?, ?, ?, ?, 'active')""", (copy_id, user_id, today, due_date.isoformat()))

            loan_id = cur.lastrowid

            cur.execute("UPDATE BookCopies SET status = 'loaned' WHERE copy_id = ?", (copy_id,))

            cur.execute("INSERT INTO AuditLog(user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)", (librarian_id, ACTION_ISSUE_LOAN, "Loans", loan_id))

        return loan_id, due_date.isoformat()

    finally:
        con.close()
            
def return_loan(loan_id, librarian_id, today):
    con = get_connection()

    try:
        cur = con.cursor()

        cur.execute("""SELECT Loans.status, Loans.due_date, Loans.copy_id, Users.role_id
                    FROM Loans JOIN Users ON Loans.user_id = Users.user_id WHERE Loans.loan_id = ?""", (loan_id,))

        row = cur.fetchone()

        if row is None:
            raise ValueError("Loan not found.")

        if row["status"] == "returned":
            raise ValueError("Loan has already been returned.")
        
        days_late = (date.fromisoformat(today) - date.fromisoformat(row["due_date"])).days

        if days_late < 0:
            days_late = 0

        fine_amount = 0.0

        # lost books already received a max fine when marked lost
        if row["status"] == "active":
            closed_days = fines.get_closed_days(cur)
            chargeable_days = fines.count_chargeable_days(row["due_date"], today, closed_days)
            rule = fines.get_fine_rule(cur, row["role_id"])
            fine_amount = fines.calculate_fine(chargeable_days, rule)

        with con:
            cur.execute("UPDATE Loans SET status = 'returned', return_date = ? WHERE loan_id = ?", (today, loan_id))

            # prevents resetting status if the copy was discarded while on loan
            cur.execute("UPDATE BookCopies SET status = 'available' WHERE copy_id = ? AND status != 'discarded'", (row["copy_id"],))

            cur.execute("INSERT INTO AuditLog(user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)", (librarian_id, ACTION_RETURN_LOAN, "Loans", loan_id))

            if fine_amount > 0:
                fines.add_fine(cur, loan_id, fine_amount, today, librarian_id)

        return days_late, fine_amount
    
    finally:
        con.close()

def mark_lost(loan_id, librarian_id, today):
    con = get_connection()

    try:
        cur = con.cursor()

        cur.execute("""SELECT Loans.status, Loans.copy_id, Users.role_id
                    FROM Loans JOIN Users ON Loans.user_id = Users.user_id WHERE Loans.loan_id = ?""", (loan_id,))

        row = cur.fetchone()

        if row is None:
            raise ValueError("Loan not found.")

        if row["status"] != "active":
            raise ValueError("Only active loans can be marked as lost.")

        rule = fines.get_fine_rule(cur, row["role_id"])

        fine_amount = rule["max_amount"]

        with con:
            cur.execute("UPDATE Loans SET status = 'lost' WHERE loan_id = ?", (loan_id,))

            cur.execute("UPDATE BookCopies SET status = 'lost' WHERE copy_id = ?", (row["copy_id"],))

            cur.execute("INSERT INTO AuditLog(user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)", (librarian_id, ACTION_MARK_LOST, "Loans", loan_id))

            fines.add_fine(cur, loan_id, fine_amount, today, librarian_id)

        return fine_amount

    finally:
        con.close()