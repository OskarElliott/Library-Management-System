# checks whether the library system's main reads work with a large volume of data
# run on a fresh seed, then reseed afterwards to restore the normal test data
import time
from datetime import date, timedelta
from db.connection import get_connection
from services import books, loans, users, fines, audit

TARGET_TITLES = 2000
TARGET_BORROWERS = 350
TARGET_LOANS = 2000
ACTIVE_LOANS = 150
MAX_SECONDS = 1
RUNS = 3

BORROWER_COUNT_SQL = """SELECT COUNT(*) FROM Users
                        JOIN Roles ON Users.role_id = Roles.role_id
                        WHERE Roles.role_name IN ('student', 'teacher') AND Users.is_active = 1"""

def check(test_id, description, passed):
    if passed:
        result = "pass"
    else:
        result = "FAIL"

    print(f"{test_id} {result}: {description}")

def count(cur, sql):
    cur.execute(sql)
    return cur.fetchone()[0]

def add_titles(cur):
    existing = count(cur, "SELECT COUNT(*) FROM Books")
    cur.execute("SELECT genre_id FROM Genres LIMIT 1")
    genre_id = cur.fetchone()[0]
    cur.execute("SELECT author_id FROM Authors LIMIT 1")
    author_id = cur.fetchone()[0]

    copy_ids = []

    for n in range(existing + 1, TARGET_TITLES + 1):
        isbn = "978" + str(n).zfill(10)
        title = f"Volume Test {n}"
        cur.execute("INSERT INTO Books(isbn, title, genre_id) VALUES (?, ?, ?)", (isbn, title, genre_id))
        book_id = cur.lastrowid
        cur.execute("INSERT INTO BookAuthors(book_id, author_id) VALUES (?, ?)", (book_id, author_id))
        cur.execute("INSERT INTO BookCopies(book_id, purchase_date) VALUES (?, ?)", (book_id, date.today().isoformat()))
        copy_ids.append(cur.lastrowid)

    return copy_ids

def add_borrowers(cur):
    existing = count(cur, BORROWER_COUNT_SQL)
    cur.execute("SELECT role_id FROM Roles WHERE role_name = 'student'")
    role_id = cur.fetchone()[0]
    cur.execute("SELECT homeroom FROM Homerooms LIMIT 1")
    homeroom = cur.fetchone()[0]

    user_ids = []

    for n in range(existing + 1, TARGET_BORROWERS + 1):
        cur.execute("INSERT INTO Users(role_id, first_name, last_name) VALUES (?, ?, ?)", (role_id, "Volume", f"Student {n}"))
        user_id = cur.lastrowid
        cur.execute("INSERT INTO StudentProfiles(user_id, homeroom) VALUES (?, ?)", (user_id, homeroom))
        user_ids.append(user_id)

    return user_ids

def add_loans(cur, copy_ids, user_ids, today):
    existing = count(cur, "SELECT COUNT(*) FROM Loans")

    # returned loans until the total reaches the target
    for i in range(TARGET_LOANS - existing):
        copy_id = copy_ids[i % len(copy_ids)]
        user_id = user_ids[i % len(user_ids)]
        checkout_date = today - timedelta(days=30 + i % 300)
        due_date = checkout_date + timedelta(days=14)
        return_date = due_date - timedelta(days=1)

        cur.execute("""INSERT INTO Loans(copy_id, user_id, checkout_date, due_date, return_date, status)
                    VALUES (?, ?, ?, ?, ?, 'returned')""",(copy_id, user_id, checkout_date.isoformat(), due_date.isoformat(), return_date.isoformat()))

    # active loans, each on its own copy and borrower
    for i in range(ACTIVE_LOANS):
        copy_id = copy_ids[i]
        user_id = user_ids[i]
        checkout_date = today - timedelta(days=i % 40)
        due_date = checkout_date + timedelta(days=14)

        cur.execute("""INSERT INTO Loans(copy_id, user_id, checkout_date, due_date, return_date, status)
                    VALUES (?, ?, ?, ?, NULL, 'active')""",(copy_id, user_id, checkout_date.isoformat(), due_date.isoformat()))
        cur.execute("UPDATE BookCopies SET status = 'loaned' WHERE copy_id = ?", (copy_id,))

def check_counts(cur):
    title_count = count(cur, "SELECT COUNT(*) FROM Books")
    borrower_count = count(cur, BORROWER_COUNT_SQL)
    loan_count = count(cur, "SELECT COUNT(*) FROM Loans")

    check("V1", f"titles: {title_count} (target at least {TARGET_TITLES})", title_count >= TARGET_TITLES)
    check("V1", f"active borrowers: {borrower_count} (target at least {TARGET_BORROWERS})", borrower_count >= TARGET_BORROWERS)
    check("V1", f"loans: {loan_count} (target at least {TARGET_LOANS + ACTIVE_LOANS})", loan_count >= TARGET_LOANS + ACTIVE_LOANS)

def time_read(name, function, *args):
    slowest = 0

    for _ in range(RUNS):
        start = time.perf_counter()
        function(*args)
        elapsed = time.perf_counter() - start
        slowest = max(slowest, elapsed)

    check("V2", f"{name} completes in under {MAX_SECONDS} second (slowest: {slowest:.3f}s)", slowest < MAX_SECONDS)

def time_reads(today_text, borrower_id):
    time_read("get_all_books", books.get_all_books)
    time_read("get_active_loans", loans.get_active_loans, today_text)
    time_read("get_overdue_loans", loans.get_overdue_loans, today_text)
    time_read("get_borrowers", users.get_borrowers)
    time_read("get_unpaid_fines", fines.get_unpaid_fines)
    time_read("get_audit_log", audit.get_audit_log)
    time_read("check_eligibility", loans.check_eligibility, borrower_id)

def main():
    con = get_connection()

    try:
        cur = con.cursor()

        if (
            count(cur, "SELECT COUNT(*) FROM Books") >= TARGET_TITLES
            or count(cur, BORROWER_COUNT_SQL) >= TARGET_BORROWERS
            or count(cur, "SELECT COUNT(*) FROM Loans") >= TARGET_LOANS
        ):
            print("Run synthetic_data_generator.py before running the volume test.")
            return

        with con:
            copy_ids = add_titles(cur)
            user_ids = add_borrowers(cur)
            add_loans(cur, copy_ids, user_ids, date.today())
            check_counts(cur)
    finally:
        con.close()

    time_reads(date.today().isoformat(), user_ids[0])


if __name__ == "__main__":
    main()
