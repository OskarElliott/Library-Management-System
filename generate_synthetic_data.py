import os
import random
from datetime import date, timedelta

import bcrypt

from db.connection import DB_PATH, init_db, get_connection

random.seed(42)

# how much data to make
NUM_STUDENTS = 50
NUM_TEACHERS = 5
NUM_BOOKS = 200
NUM_HISTORICAL_LOANS = 800
NUM_ACTIVE_LOANS = 30
NUM_RESERVATIONS = 15

SHARED_PASSWORD = "library123"
TODAY = date.today()

# roles
ROLES = [(1, "librarian"), (2, "teacher"), (3, "student")]

# fine rules per role, PLN. no rule for librarian (never fined)
FINE_RULES = [
    # role_id, grace_days, tier_1_rate, tier_2_rate, max_amount
    (2, 7, 0.25, 0.50, 20.00),
    (3, 3, 0.50, 1.00, 30.00),
]

LOAN_DAYS = {"teacher": 28, "student": 14}

GENRES = ["Fiction", "Science Fiction", "Fantasy", "Mystery",
          "History", "Science", "Biography", "Reference"]
TRENDING_UP = "Science Fiction"
TRENDING_DOWN = "Reference"
SEASONAL = "History"  # spikes in spring

# sci-fi and fantasy sit under fiction to exercise the genre hierarchy
SUBGENRES = {"Science Fiction": "Fiction", "Fantasy": "Fiction"}

# popular genres carry more copies per title
POPULAR_GENRES = {"Fiction", "Science Fiction", "Fantasy", "Mystery"}

FIRST_NAMES = ["Amara", "Liam", "Yuki", "Sofia", "Omar", "Mei", "Noah", "Priya",
               "Lukas", "Aisha", "Mateo", "Hana", "Ivan", "Zara", "Diego", "Lena",
               "Kofi", "Elena", "Arjun", "Freya", "Tariq", "Nina", "Hugo", "Leila",
               "Kenji", "Maja", "Sami", "Clara", "Pavel", "Ingrid"]
LAST_NAMES = ["Okafor", "Nowak", "Tanaka", "Garcia", "Haddad", "Chen", "Smith",
              "Patel", "Muller", "Khan", "Rossi", "Kim", "Petrov", "Ali", "Silva",
              "Larsen", "Mensah", "Costa", "Sharma", "Berg", "Hassan", "Novak",
              "Dubois", "Said", "Yamamoto", "Kowalski", "Aziz", "Bauer", "Ivanov"]

SUBJECTS = ["Mathematics", "English", "Science", "History", "Art"]

NUM_CLUSTERS = 6


def make_username(first, last, taken):
    base = f"{first}.{last}".lower()
    name = base
    n = 2
    while name in taken:
        name = f"{base}.{n}"
        n += 1
    taken.add(name)
    return name


def hashed_password():
    # all seed users share one password, so hash it once and reuse
    return bcrypt.hashpw(SHARED_PASSWORD.encode(), bcrypt.gensalt()).decode()


def month_index(d):
    # 0 = twelve months ago, 11 = this month
    return 11 - ((TODAY.year - d.year) * 12 + (TODAY.month - d.month))


def trend_weight(genre, d):
    idx = month_index(d)
    if genre == TRENDING_UP:
        return 0.4 + 0.1 * idx
    if genre == TRENDING_DOWN:
        return 1.6 - 0.1 * idx
    if genre == SEASONAL:
        return 3.0 if d.month in (3, 4, 5) else 0.6
    return 1.0


def fine_amount(role_name, days_overdue):
    rule = next((r for r in FINE_RULES
                 if r[0] == dict((b, a) for a, b in ROLES)[role_name]), None)
    if rule is None:
        return 0.0
    _, grace, t1, t2, cap = rule
    chargeable = days_overdue - grace
    if chargeable <= 0:
        return 0.0
    tier1_days = min(chargeable, 7)
    tier2_days = max(chargeable - 7, 0)
    amount = tier1_days * t1 + tier2_days * t2
    return round(min(amount, cap), 2)


def seed():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
    conn = get_connection()
    cur = conn.cursor()
    pw = hashed_password()

    # roles
    cur.executemany("INSERT INTO Roles(role_id, role_name) VALUES (?, ?)", ROLES)

    # fine rules
    cur.executemany(
        "INSERT INTO FineRules(role_id, grace_days, tier_1_rate, tier_2_rate, max_amount) "
        "VALUES (?, ?, ?, ?, ?)", FINE_RULES)

    # genres, parents first so the self-reference resolves
    genre_id = {}
    for name in GENRES:
        if name not in SUBGENRES:
            cur.execute("INSERT INTO Genres(name) VALUES (?)", (name,))
            genre_id[name] = cur.lastrowid
    for name, parent in SUBGENRES.items():
        cur.execute("INSERT INTO Genres(name, parent_genre_id) VALUES (?, ?)",
                    (name, genre_id[parent]))
        genre_id[name] = cur.lastrowid

    # publishers
    publishers = ["Penguin", "HarperCollins", "Oxford UP", "Bloomsbury", "Vintage"]
    pub_ids = []
    for name in publishers:
        cur.execute("INSERT INTO Publishers(name, country) VALUES (?, ?)",
                    (name, random.choice(["UK", "US", "PL"])))
        pub_ids.append(cur.lastrowid)

    # authors
    author_ids = []
    for _ in range(60):
        cur.execute("INSERT INTO Authors(first_name, last_name) VALUES (?, ?)",
                    (random.choice(FIRST_NAMES), random.choice(LAST_NAMES)))
        author_ids.append(cur.lastrowid)

    # books + copies
    books = []  # (book_id, genre_name, popularity)
    copies_by_book = {}
    for i in range(NUM_BOOKS):
        genre = random.choice(GENRES)
        isbn = "978" + "".join(random.choice("0123456789") for _ in range(10))
        cur.execute(
            "INSERT INTO Books(isbn, title, publication_year, publisher_id, genre_id, "
            "description, replacement_cost) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (isbn, f"Sample Book {i+1}", random.randint(1990, 2024),
             random.choice(pub_ids), genre_id[genre],
             "placeholder description", round(random.uniform(20, 120), 2)))
        book_id = cur.lastrowid
        cur.execute("INSERT INTO BookAuthors(book_id, author_id) VALUES (?, ?)",
                    (book_id, random.choice(author_ids)))

        # top 20% of books are 'popular' (pareto)
        popularity = 5 if random.random() < 0.20 else 1
        books.append((book_id, genre, popularity))

        if genre in POPULAR_GENRES:
            n_copies = random.randint(3, 5)
        else:
            n_copies = random.randint(1, 2)
        ids = []
        for _ in range(n_copies):
            cur.execute(
                "INSERT INTO BookCopies(book_id, purchase_date, condition, status) "
                "VALUES (?, ?, ?, 'available')",
                (book_id, str(TODAY - timedelta(days=random.randint(30, 1500))),
                 random.choice(["new", "good", "worn"])))
            ids.append(cur.lastrowid)
        copies_by_book[book_id] = ids

    # cluster preferences: each cluster likes two genres
    cluster_prefs = {c: random.sample(GENRES, 2) for c in range(NUM_CLUSTERS)}

    # users
    taken = set()
    students = []  # (user_id, cluster)
    teachers = []
    for _ in range(NUM_STUDENTS):
        first, last = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)
        username = make_username(first, last, taken)
        cur.execute("INSERT INTO Users(username, password_hash, role_id, email) "
                    "VALUES (?, ?, 3, ?)", (username, pw, f"{username}@school.edu"))
        uid = cur.lastrowid
        year = random.choice([7, 8, 9, 10, 11, 12, 13])
        cur.execute("INSERT INTO StudentProfiles(user_id, year_number, homeroom, "
                    "form_tutor_email) VALUES (?, ?, ?, ?)",
                    (uid, year, f"{year}A", f"tutor.{year}@school.edu"))
        students.append((uid, random.randrange(NUM_CLUSTERS)))

    for _ in range(NUM_TEACHERS):
        first, last = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)
        username = make_username(first, last, taken)
        cur.execute("INSERT INTO Users(username, password_hash, role_id, email) "
                    "VALUES (?, ?, 2, ?)", (username, pw, f"{username}@school.edu"))
        uid = cur.lastrowid
        cur.execute("INSERT INTO StaffProfiles(user_id, subject) VALUES (?, ?)",
                    (uid, random.choice(SUBJECTS)))
        teachers.append(uid)

    cur.execute("INSERT INTO Users(username, password_hash, role_id, email) "
                "VALUES ('admin.librarian', ?, 1, 'librarian@school.edu')", (pw,))
    librarian_id = cur.lastrowid
    cur.execute("INSERT INTO StaffProfiles(user_id, subject) VALUES (?, NULL)",
                (librarian_id,))

    # helper to pick a book for a borrower on a given date
    books_by_genre = {}
    for b in books:
        books_by_genre.setdefault(b[1], []).append(b)

    def pick_book(cluster, d):
        weights = []
        for g in GENRES:
            w = trend_weight(g, d)
            if g in cluster_prefs[cluster]:
                w *= 4
            weights.append(w)
        genre = random.choices(GENRES, weights=weights)[0]
        pool = books_by_genre.get(genre, books)
        pops = [b[2] for b in pool]
        return random.choices(pool, weights=pops)[0][0]

    # historical (returned) loans
    for _ in range(NUM_HISTORICAL_LOANS):
        uid, cluster = random.choice(students)
        checkout = TODAY - timedelta(days=random.randint(20, 360))
        book_id = pick_book(cluster, checkout)
        copy_id = random.choice(copies_by_book[book_id])
        due = checkout + timedelta(days=LOAN_DAYS["student"])
        # most on time, some late
        late = random.random() < 0.20
        returned = due + timedelta(days=random.randint(1, 25) if late else
                                   -random.randint(0, 10))
        if returned > TODAY:
            returned = TODAY
        cur.execute("INSERT INTO Loans(copy_id, user_id, checkout_date, due_date, "
                    "return_date, status) VALUES (?, ?, ?, ?, ?, 'returned')",
                    (copy_id, uid, str(checkout), str(due), str(returned)))
        loan_id = cur.lastrowid
        overdue = (returned - due).days
        amount = fine_amount("student", overdue)
        if amount > 0:
            # historical fines mostly paid off
            status = "paid" if random.random() < 0.8 else "unpaid"
            paid = str(returned) if status == "paid" else None
            cur.execute("INSERT INTO Fines(loan_id, amount, issued_date, paid_date, "
                        "status) VALUES (?, ?, ?, ?, ?)",
                        (loan_id, amount, str(due), paid, status))

    # active loans: mix of on-time, overdue, long-overdue
    for i in range(NUM_ACTIVE_LOANS):
        uid, cluster = random.choice(students)
        if i % 3 == 0:
            checkout = TODAY - timedelta(days=random.randint(0, 10))   # on time
        elif i % 3 == 1:
            checkout = TODAY - timedelta(days=random.randint(18, 30))  # overdue
        else:
            checkout = TODAY - timedelta(days=random.randint(45, 90))  # long overdue
        book_id = pick_book(cluster, checkout)
        copy_id = random.choice(copies_by_book[book_id])
        due = checkout + timedelta(days=LOAN_DAYS["student"])
        cur.execute("INSERT INTO Loans(copy_id, user_id, checkout_date, due_date, "
                    "return_date, status) VALUES (?, ?, ?, ?, NULL, 'active')",
                    (copy_id, uid, str(checkout), str(due)))
        loan_id = cur.lastrowid
        cur.execute("UPDATE BookCopies SET status='loaned' WHERE copy_id=?", (copy_id,))
        overdue = (TODAY - due).days
        amount = fine_amount("student", overdue)
        if amount > 0:
            cur.execute("INSERT INTO Fines(loan_id, amount, issued_date, status) "
                        "VALUES (?, ?, ?, 'unpaid')", (loan_id, amount, str(due)))
            cur.execute("INSERT INTO Notifications(loan_id, recipient_id, "
                        "notification_type, recipient_email, sent_at, status) "
                        "VALUES (?, ?, 'overdue_warning', ?, ?, 'sent')",
                        (loan_id, uid, f"user{uid}@school.edu", str(TODAY)))

    # reservations on loaned-out books, mixed states
    loaned_books = list({row[0] for row in
                         conn.execute("SELECT book_id FROM BookCopies "
                                      "WHERE status='loaned'")})
    states = ["pending", "ready", "fulfilled", "expired", "cancelled"]
    for i in range(NUM_RESERVATIONS):
        if not loaned_books:
            break
        book_id = random.choice(loaned_books)
        uid, _ = random.choice(students)
        req = TODAY - timedelta(days=random.randint(1, 20))
        status = states[i % len(states)]
        notified = expires = None
        if status in ("ready", "expired"):
            notified = str(req + timedelta(days=2))
            expires = str(req + timedelta(days=4))
        cur.execute("INSERT INTO Reservations(book_id, user_id, request_date, "
                    "priority, status, notified_date, expires_at) "
                    "VALUES (?, ?, ?, 2, ?, ?, ?)",
                    (book_id, uid, str(req), status, notified, expires))
        if status == "ready":
            cur.execute("INSERT INTO Notifications(recipient_id, notification_type, "
                        "recipient_email, sent_at, status) "
                        "VALUES (?, 'reservation_ready', ?, ?, 'sent')",
                        (uid, f"user{uid}@school.edu", notified))

    # school calendar for the last ~12 months
    day = TODAY - timedelta(days=365)
    while day <= TODAY:
        if day.weekday() >= 5:
            day_type, is_open = "weekend", 0
        elif day.month == 12 and day.day >= 18:
            day_type, is_open = "holiday", 0
        elif day.month == 4 and day.day <= 7:
            day_type, is_open = "holiday", 0
        else:
            day_type, is_open = "school_day", 1
        cur.execute("INSERT INTO SchoolCalendar(day_date, is_open, day_type) "
                    "VALUES (?, ?, ?)", (str(day), is_open, day_type))
        day += timedelta(days=1)

    # a few audit log entries by the librarian
    for action in ["create_user", "add_book", "adjust_fine"]:
        cur.execute("INSERT INTO AuditLog(user_id, action, table_name, record_id) "
                    "VALUES (?, ?, ?, ?)", (librarian_id, action, "Books", 1))

    conn.commit()
    conn.close()
    print("seed complete")


if __name__ == "__main__":
    seed()
