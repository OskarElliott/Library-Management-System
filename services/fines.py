from datetime import date, timedelta

def count_chargeable_days(due_date, return_date, closed_days):
    due = date.fromisoformat(due_date)
    returned = date.fromisoformat(return_date)

    days = 0
    day = due + timedelta(days=1)

    while day <= returned:
        if day.weekday() < 5 and day.isoformat() not in closed_days:
            days += 1
        day += timedelta(days=1)

    return days

def calculate_fine(chargeable_days, rule):
    days_to_charge = chargeable_days - rule["grace_days"]

    if days_to_charge <= 0:
        return 0.0

    tier_1_days = min(days_to_charge, rule["tier_1_days"])
    tier_2_days = days_to_charge - tier_1_days

    amount = (tier_1_days * rule["tier_1_rate"] + tier_2_days * rule["tier_2_rate"])

    return round(min(amount, rule["max_amount"]), 2)

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
    cur.execute("INSERT INTO Fines(loan_id, amount, issued_date, status) VALUES(?,?,?,'unpaid')", (loan_id, amount, today))

    fine_id = cur.lastrowid

    cur.execute("""INSERT INTO AuditLog(user_id, action, table_name, record_id) VALUES(?, 'add_fine', 'Fines', ?)""", (librarian_id, fine_id))