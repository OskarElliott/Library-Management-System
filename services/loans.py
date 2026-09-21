from db.connection import get_connection

def get_active_loans(today):
    con = get_connection()
    cur = con.cursor()

    cur.execute("""SELECT Loans.loan_id, Users.first_name, Users.last_name, Books.title, Loans.copy_id, Loans.checkout_date, Loans.due_date, julianday(Loans.due_date) - julianday(?) AS days_remaining
                FROM Loans JOIN BookCopies ON Loans.copy_id = BookCopies.copy_id
                JOIN Books ON BookCopies.book_id = Books.book_id
                JOIN Users ON Loans.user_id = Users.user_id
                WHERE Loans.status = 'active' ORDER BY Loans.due_date ASC""", (today,))

    rows = cur.fetchall()
    con.close()
    return rows

def get_overdue_loans(today):
    con = get_connection()
    cur = con.cursor()

    cur.execute("""SELECT Loans.loan_id, Users.first_name, Users.last_name, Books.title, Loans.copy_id, Loans.checkout_date, Loans.due_date, julianday(?) - julianday(Loans.due_date) AS days_overdue
                FROM Loans JOIN BookCopies ON Loans.copy_id = BookCopies.copy_id
                JOIN Books ON BookCopies.book_id = Books.book_id
                JOIN Users ON Loans.user_id = Users.user_id WHERE Loans.status = 'active' AND Loans.due_date < ?
                ORDER BY days_overdue DESC""", (today, today))
    
    rows = cur.fetchall()
    con.close()
    return rows

