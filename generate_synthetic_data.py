import random
import bcrypt
from db.connection import get_connection, init_db, DB_PATH
from datetime import date, timedelta

TODAY = date(2026, 6, 1)        # fixed so runs are reproducible and the video demo is stable

random.seed(42)  # reproducible runs

DEV_PASSWORD = "library123"
PASSWORD_HASH = bcrypt.hashpw(DEV_PASSWORD.encode(), bcrypt.gensalt()).decode()  # hash once, reuse

# wipe and rebuild so every run starts clean
DB_PATH.unlink(missing_ok=True)
init_db()
conn = get_connection()

# roles
roles = [
    (1, "student", "library member, standard borrowing"),
    (2, "teacher", "staff, extended borrowing"),
    (3, "librarian", "system administrator"),
]
conn.executemany("INSERT INTO Roles (role_id, role_name, description) VALUES (?, ?, ?)", roles)

# per-role fine rules: grace_days, tier_1_rate, tier_2_rate, max_amount (pln)
fine_rules = [
    (1, 1, 3, 0.50, 1.00, 20.00),  # student
    (2, 2, 7, 0.00, 0.00, 0.00),   # teacher: exempt
    (3, 3, 7, 0.00, 0.00, 0.00),   # librarian: exempt
]
conn.executemany(
    "INSERT INTO FineRules (rule_id, role_id, grace_days, tier_1_rate, tier_2_rate, max_amount) VALUES (?, ?, ?, ?, ?, ?)",
    fine_rules,
)
conn.commit()

# Generic name pools
FIRST_NAMES = ["Oliver", "Emily", "George", "Olivia", "Harry", "Charlotte", "Jack", "Amelia",
               "Thomas", "Sophie", "William", "Grace", "James", "Ella", "Henry", "Lucy",
               "Noah", "Chloe", "Liam", "Emma", "Lucas", "Hannah", "Benjamin", "Isla"]

LAST_NAMES = ["Smith", "Jones", "Williams", "Brown", "Taylor", "Wilson", "Johnson", "Davies",
              "Evans", "Thomas", "Roberts", "Walker", "Wright", "Thompson", "White", "Harris",
              "Martin", "Clark", "Lewis", "Young", "King", "Scott", "Green", "Baker"]

used_usernames = set()

def make_username(first, last):
    base = f"{first}.{last}".lower()
    username = base
    n = 2
    while username in used_usernames:  # .2, .3 on collision
        username = f"{base}.{n}"
        n += 1
    used_usernames.add(username)
    return username

def insert_user(first, last, role_id):
    username = make_username(first, last)
    email = f"{username}@school.edu"
    cur = conn.execute(
        "INSERT INTO Users (username, password_hash, role_id, email) VALUES (?, ?, ?, ?)",
        (username, PASSWORD_HASH, role_id, email),
    )
    return cur.lastrowid  # need the id for loans later

librarian_id = insert_user("Grace", "Holloway", 3)

teacher_ids = []
for _ in range(5):
    teacher_ids.append(insert_user(random.choice(FIRST_NAMES), random.choice(LAST_NAMES), 2))

YEARS = [7, 8, 9, 10, 11, 12, 13]  # ib1/ib2 = 12/13

student_ids = []
for year in YEARS:
    homeroom = f"{year}A"  # one class per year for now
    tutor_email = f"tutor.y{year}@school.edu"
    for _ in range(7):
        uid = insert_user(random.choice(FIRST_NAMES), random.choice(LAST_NAMES), 1)
        conn.execute(
            "INSERT INTO StudentProfiles (user_id, year_number, homeroom, form_tutor_email) VALUES (?, ?, ?, ?)",
            (uid, year, homeroom, tutor_email),
        )
        student_ids.append(uid)

conn.commit()

# publishers
PUBLISHERS = ["Penguin", "Oxford UP", "HarperCollins", "Macmillan", "Vintage", "Pearson"]
publisher_ids = []
for name in PUBLISHERS:
    cur = conn.execute("INSERT INTO Publishers (name) VALUES (?)", (name,))
    publisher_ids.append(cur.lastrowid)

# genre: (name, book_count, copy_min, copy_max) -- counts and copies scale with popularity
GENRE_SPEC = [
    ("Fiction", 35, 3, 5),
    ("Science Fiction", 35, 3, 5),
    ("Fantasy", 35, 3, 5),
    ("History", 25, 2, 3),
    ("Biography", 25, 2, 3),
    ("Science", 25, 2, 3),
    ("Poetry", 10, 1, 2),
    ("Reference", 10, 1, 2),
]
genre_ids = {}
for name, _, _, _ in GENRE_SPEC:
    cur = conn.execute("INSERT INTO Genres (name) VALUES (?)", (name,))
    genre_ids[name] = cur.lastrowid

# recurring author pool so some authors write several books (exercises the m:n link)
author_ids = []
for _ in range(40):
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    cur = conn.execute("INSERT INTO Authors (first_name, last_name) VALUES (?, ?)", (first, last))
    author_ids.append(cur.lastrowid)

# titles are generic on purpose, realism here doesn't affect the demand signal
TITLE_ADJ = ["Silent", "Hidden", "Last", "Broken", "Golden", "Distant", "Lost", "Burning", "Quiet", "Endless"]
TITLE_NOUN = ["River", "Empire", "Shadow", "Garden", "Machine", "Promise", "Voyage", "Mirror", "Throne", "Signal"]
TITLE_PLACE = ["Tokyo", "the North", "Marrakesh", "the Deep", "Vienna", "the Stars", "Lisbon", "the Frontier"]

def make_title():
    pattern = random.randint(0, 2)
    if pattern == 0:
        return f"The {random.choice(TITLE_ADJ)} {random.choice(TITLE_NOUN)}"
    if pattern == 1:
        return f"{random.choice(TITLE_NOUN)} of {random.choice(TITLE_PLACE)}"
    return f"A {random.choice(TITLE_NOUN)} in {random.choice(TITLE_PLACE)}"

isbn_counter = 1
book_ids = []
book_genre = {}  # book_id -> genre name, used when grouping books for loans

for name, count, copy_min, copy_max in GENRE_SPEC:
    for _ in range(count):
        isbn = f"978{isbn_counter:010d}"  # synthetic, no check digit
        isbn_counter += 1
        year = random.randint(1990, 2025)
        cost = round(random.uniform(25, 90), 2)  # pln, lost-copy charge
        cur = conn.execute(
            "INSERT INTO Books (isbn, title, publication_year, publisher_id, genre_id, replacement_cost) VALUES (?, ?, ?, ?, ?, ?)",
            (isbn, make_title(), year, random.choice(publisher_ids), genre_ids[name], cost),
        )
        book_id = cur.lastrowid
        book_ids.append(book_id)
        book_genre[book_id] = name

        for author_id in random.sample(author_ids, random.randint(1, 2)):
            conn.execute("INSERT INTO BookAuthors (book_id, author_id) VALUES (?, ?)", (book_id, author_id))

        for _ in range(random.randint(copy_min, copy_max)):
            conn.execute("INSERT INTO BookCopies (book_id) VALUES (?)", (book_id,))

conn.commit()

# genre popularity: bigger weight = borrowed more, so the demand score has a clear ranking
GENRE_POPULARITY = {
    "Fiction": 5,
    "Science Fiction": 5,
    "Fantasy": 4,
    "History": 3,
    "Biography": 3,
    "Science": 3,
    "Poetry": 1,
    "Reference": 1,
}
GENRE_NAMES = list(GENRE_POPULARITY.keys())
GENRE_WEIGHTS = list(GENRE_POPULARITY.values())

# top 20% of books are "popular" and get borrowed far more (pareto)
random.shuffle(book_ids)
split = int(len(book_ids) * 0.2)
popular_books = set(book_ids[:split])

# group book ids by genre once, so the loop isn't re-filtering 200 books each time
books_by_genre = {}
for book_id, genre in book_genre.items():
    books_by_genre.setdefault(genre, []).append(book_id)

# ~800 historical loans over the past 12 months, all returned
for _ in range(800):
    student_id = random.choice(student_ids)
    genre = random.choices(GENRE_NAMES, weights=GENRE_WEIGHTS)[0]

    candidates = books_by_genre[genre]
    weights = [8 if b in popular_books else 1 for b in candidates]
    book_id = random.choices(candidates, weights=weights)[0]

    copy_id = conn.execute(
        "SELECT copy_id FROM BookCopies WHERE book_id = ? ORDER BY RANDOM() LIMIT 1", (book_id,)
    ).fetchone()["copy_id"]

    days_ago = random.randint(0, 364)
    checkout = TODAY - timedelta(days=days_ago)
    due = checkout + timedelta(days=14)
    returned = checkout + timedelta(days=random.randint(3, 14))

    conn.execute(
        "INSERT INTO Loans (copy_id, user_id, checkout_date, due_date, return_date, status) VALUES (?, ?, ?, ?, ?, 'returned')",
        (copy_id, student_id, checkout.isoformat(), due.isoformat(), returned.isoformat()),
    )

conn.commit()