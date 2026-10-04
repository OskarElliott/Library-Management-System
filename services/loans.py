from db.connection import get_connection
from services import users
from datetime import date, timedelta

def get_active_loans(today):
    con = get_connection()
    cur = con.cursor()

    cur.execute("""SELECT Loans.loan_id, Users.first_name, Users.last_name, Books.title, Loans.copy_id, Loans.checkout_date, Loans.due_date, julianday(Loans.due_date) - julianday(?) AS days_remaining
                FROM Loans JOIN BookCopies ON Loans.copy_id = BookCopies.copy_id JOIN Books ON BookCopies.book_id = Books.book_id
                JOIN Users ON Loans.user_id = Users.user_id
                WHERE Loans.status = 'active' ORDER BY Loans.due_date ASC""", (today,))

    rows = cur.fetchall()
    con.close()
    return rows

def get_overdue_loans(today):
    con = get_connection()
    cur = con.cursor()

    cur.execute("""SELECT Loans.loan_id, Users.first_name, Users.last_name, Books.title, Loans.copy_id, Loans.checkout_date, Loans.due_date, julianday(?) - julianday(Loans.due_date) AS days_overdue
                FROM Loans JOIN BookCopies ON Loans.copy_id = BookCopies.copy_id JOIN Books ON BookCopies.book_id = Books.book_id
                JOIN Users ON Loans.user_id = Users.user_id
                WHERE Loans.status = 'active' AND Loans.due_date < ? ORDER BY days_overdue DESC""", (today, today))

    rows = cur.fetchall()
    con.close()
    return rows

def check_eligibility(user_id):
    user = users.get_user(user_id)

    con = get_connection()
    cur = con.cursor()

    cur.execute("SELECT active_loans, outstanding_fines FROM BorrowingEligibility WHERE  user_id = ?", (user_id,))

    row = cur.fetchone()
    con.close()

    reasons = []

    if not user.get_is_active():
        reasons.append("Account is inactive.")

    if row["active_loans"] >= user.MAX_LOANS:
        reasons.append(f"Borrower has reached the loan limit ({row['active_loans']} of {user.MAX_LOANS} loans)")
    if row["outstanding_fines"] > 0:
        reasons.append(f"Borrower has outstanding fines of {row['outstanding_fines']} PLN.")

    return reasons

def issue_loan(copy_id, user_id, librarian_id, today):
    reasons = check_eligibility(user_id)

    if reasons: 
        raise ValueError("\n".join(reasons))

    con = get_connection()
    cur = con.cursor()

    cur.execute("SELECT status FROM BookCopies WHERE copy_id = ?", (copy_id,))

    row = cur.fetchone()

    if row is None:
        con.close()
        raise ValueError("Copy not found.")

    if row["status"] != "available":
        con.close()
        raise ValueError("Copy is unavailable.")

    user = users.get_user(user_id)
    due_date = date.fromisoformat(today) + timedelta(days=user.MAX_LOAN_DAYS)

    with con:
        cur.execute("""INSERT INTO Loans (copy_id, user_id, checkout_date, due_date, status)
                        VALUES (?,?,?,?, 'active')""", (copy_id, user_id, today, due_date.isoformat()))

        loan_id = cur.lastrowid

        cur.execute("UPDATE BookCopies SET status = 'loaned' WHERE copy_id = ?", (copy_id,))

        cur.execute("""INSERT INTO AuditLog (user_id, action, table_name, record_id) 
                        VALUES (?, 'issue_loan', 'Loans', ?)""", (librarian_id, loan_id))

    con.close()
    return loan_id, due_date.isoformat()

def return_loan(loan_id, librarian_id, today):
    con = get_connection()
    cur = con.cursor()

    cur.execute("SELECT status, due_date, copy_id FROM Loans WHERE loan_id = ?", (loan_id,))

    row = cur.fetchone()

    if row is None:
        con.close()
        raise ValueError("Loan not found.")

    if row["status"] == "returned":
        con.close()
        raise ValueError("Loan has already been returned.")

    days_late = (date.fromisoformat(today) - date.fromisoformat(row["due_date"])).days

    if days_late < 0:
        days_late = 0

    with con:
        cur.execute("UPDATE Loans SET status = 'returned', return_date = ? WHERE loan_id = ?", (today, loan_id))

        cur.execute("UPDATE BookCopies SET status = 'available' WHERE copy_id = ?", (row["copy_id"],))

        cur.execute("INSERT INTO AuditLog (user_id, action, table_name, record_id) VALUES (?, 'return_loan', 'Loans', ?)", (librarian_id, loan_id))

    con.close()
    return days_late

def mark_lost(loan_id, librarian_id):
    con = get_connection()
    cur = con.cursor()

    cur.execute("SELECT status, copy_id FROM Loans WHERE loan_id = ?", (loan_id,))

    row = cur.fetchone()

    if row is None:
        con.close()
        raise ValueError("Loan not found.")

    if row["status"] != "active":
        con.close()
        raise ValueError("Only active loans can be marked as lost.")

    with con:
        cur.execute("UPDATE Loans SET status = 'lost' WHERE loan_id = ?", (loan_id,))

        cur.execute("UPDATE BookCopies SET status = 'lost' WHERE copy_id = ?", (row["copy_id"],))

        cur.execute("INSERT INTO AuditLog (user_id, action, table_name, record_id) VALUES (?, 'mark_lost', 'Loans', ?)", (librarian_id, loan_id))

    con.close()


        