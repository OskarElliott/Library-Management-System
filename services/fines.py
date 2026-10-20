from datetime import date, timedelta
from db.connection import get_connection

ACTION_ADD_FINE = "add_fine"
ACTION_RECORD_PAYMENT = "record_payment"

def count_chargeable_days(due_date, return_date, closed_days):
    due = date.fromisoformat(due_date)
    returned = date.fromisoformat(return_date)

    days = 0
    day = due + timedelta(days=1) # fines start the day after the due date

    while day <= returned:
        if day.weekday() < 5 and day.isoformat() not in closed_days: # <5 = weekdays, weekends skip automatically
            days += 1
        day += timedelta(days=1)

    return days

def calculate_fine(chargeable_days, rule):
    days_to_charge = chargeable_days - rule["grace_days"]

    if days_to_charge <= 0:
        return 0.0

    tier_1_days = min(days_to_charge, rule["tier_1_days"])
    tier_2_days = days_to_charge - tier_1_days

    amount = tier_1_days * rule["tier_1_rate"] + tier_2_days * rule["tier_2_rate"]

    if amount > rule["max_amount"]:
        amount = rule["max_amount"]

    # round to 2 decimal places to avoid storing floating point errors
    return round(amount, 2)

# uses the caller's connection, avoiding a second connection and keeping fine inserts in the caller's transaction
def get_closed_days(cur):
    cur.execute("SELECT day_date FROM ClosedDays")

    closed_days = set()

    for row in cur.fetchall():
        closed_days.add(row["day_date"])

    return closed_days

def get_fine_rule(cur, role_id):
    cur.execute("""SELECT grace_days, tier_1_days, tier_1_rate, tier_2_rate, max_amount
                    FROM FineRules WHERE role_id = ?""", (role_id,))

    return cur.fetchone()

def add_fine(cur, loan_id, amount, today, librarian_id):
    cur.execute("INSERT INTO Fines(loan_id, amount, issued_date, status) VALUES (?, ?, ?, 'unpaid')", (loan_id, amount, today))
    fine_id = cur.lastrowid

    cur.execute("INSERT INTO AuditLog(user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)", (librarian_id, ACTION_ADD_FINE, "Fines", fine_id))

def get_unpaid_fines():
    con = get_connection()

    try:
        cur = con.cursor()
        cur.execute("""SELECT Fines.fine_id, Users.first_name, Users.last_name, Books.title, Fines.amount, Fines.issued_date
                    FROM Fines JOIN Loans ON Fines.loan_id = Loans.loan_id
                    JOIN Users ON Loans.user_id = Users.user_id
                    JOIN BookCopies ON Loans.copy_id = BookCopies.copy_id
                    JOIN Books ON BookCopies.book_id = Books.book_id
                    WHERE Fines.status = 'unpaid' ORDER BY Users.last_name, Fines.issued_date""")
        rows = cur.fetchall()

    finally:
        con.close()

    return rows

def record_payment(fine_id, librarian_id, today):
    con = get_connection()

    try:
        cur = con.cursor()
        cur.execute("SELECT status FROM Fines WHERE fine_id = ?", (fine_id,))
        row = cur.fetchone()

        if row is None:
            raise ValueError("Fine not found.")

        if row["status"] == "paid":
            raise ValueError("Fine has already been paid.")

        with con:
            cur.execute("UPDATE Fines SET status = 'paid', paid_date = ? WHERE fine_id = ?", (today, fine_id))

            cur.execute("INSERT INTO AuditLog(user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)", (librarian_id, ACTION_RECORD_PAYMENT, "Fines", fine_id))
            
    finally:
        con.close()