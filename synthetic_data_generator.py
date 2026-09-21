# wipes and reseeds library.db with synthetic test data
import random
import bcrypt
from db.connection import init_db, get_connection, DB_PATH
from datetime import date, timedelta
from models.student import Student
from models.teacher import Teacher

random.seed(42) # makes randomly generated seed data reproducible 

NAMES = [ #generated via https://1000randomnames.com/
    ("Alice", "Dunn"),
    ("Dawson", "Hunter"),
    ("Khloe", "Nixon"),
    ("Cory", "Vaughan"),
    ("Nancy", "Fry"),
    ("Jacoby", "McDonald"),
    ("Daisy", "Howard"),
    ("Jeremiah", "Avalos"),
    ("Paloma", "Davidson"),
    ("Dante", "Giles"),
    ("Bailee", "Salas"),
    ("Zaiden", "Hamilton"),
    ("Mackenzie", "Byrd"),
    ("Cristian", "Ponce"),
    ("Aileen", "Harrington"),
    ("Omari", "Vega"),
    ("Dakota", "Boyer"),
    ("Zeke", "Banks"),
    ("Cali", "Gallagher"),
    ("Marcos", "Kennedy"),
    ("Brianna", "Hickman"),
    ("Jakobe", "Murphy"),
    ("Bella", "Enriquez"),
    ("Elisha", "Valenzuela"),
    ("Henley", "Hester"),
    ("Rene", "Wyatt"),
    ("Liberty", "Calhoun"),
    ("Gary", "McDowell"),
    ("Rayna", "Roberts"),
    ("Josiah", "Alexander"),
    ("Lyla", "Cabrera"),
    ("Cade", "Hull"),
    ("Andi", "McCann"),
    ("Heath", "Sullivan"),
    ("Melanie", "Santos"),
    ("Walker", "Stanton"),
    ("Jaycee", "Levy"),
    ("Harold", "Preston"),
    ("Indie", "Sanders"),
    ("Jose", "Conley"),
    ("Salem", "Lim"),
    ("Cal", "Shah"),
    ("Angelica", "Moran"),
    ("Tate", "Bradford"),
    ("Rhea", "Stanley"),
    ("Manuel", "Parks"),
    ("Ainsley", "Drake"),
    ("Jalen", "O'Donnell"),
    ("Bellamy", "Wagner"),
    ("Enzo", "Wolf"),
    ("Jolene", "Chan"),
    ("Frank", "Harris"),
    ("Penelope", "Holt"),
    ("Niko", "Sellers"),
    ("Mercy", "Fischer"),
    ("Leonidas", "Lucas"),
    ("Phoenix", "Villa"),
    ("Clay", "Andrews"),
    ("Payton", "McGuire"),
    ("Casey", "Miles"),
    ("Alessandra", "Blair"),
    ("Troy", "Phan"),
    ("Elsa", "Adams"),
    ("Hudson", "Moran"),
    ("Celeste", "Barton"),
    ("Cassius", "Randolph"),
    ("Kailey", "Friedman"),
    ("Darwin", "Wright"),
    ("Lily", "Richmond"),
    ("Mordechai", "Hart"),
    ("Gemma", "Powell"),
    ("Bennett", "James"),
    ("Quinn", "Frye"),
    ("Franco", "Gomez"),
    ("Natalie", "Terry"),
    ("Armani", "Hale"),
    ("Brinley", "Brady"),
    ("Reed", "Frost"),
    ("Paula", "Hail"),
    ("Hector", "Durham"),
]

PUBLISHERS = ["Penguin Random House", "HarperCollins", "Simon & Schuster", "Hachette Livre", "Macmillan Publishers"]

TITLES = [ # placeholder book titles, generated via https://perchance.org/book
    "For Whom the Bell Tolls",
    "The Brothers Karamazov",
    "The Color Purple",
    "The Tempest",
    "The Metamorphosis",
    "A Handful of Dust",
    "A Portrait of the Artist as a Young Man",
    "A Confederacy of Dunces",
    "The Aeneid",
    "Memoirs of Hadrian",
    "Wuthering Heights",
    "The Call of the Wild",
    "Tom Jones",
    "Paradise Lost",
    "Slaughterhouse-Five",
    "The Master and Margarita",
    "An American Tragedy",
    "Nostromo",
    "Doctor Zhivago",
    "Things Fall Apart",
    "The Remains of the Day",
    "Siddhartha",
    "The Tin Drum",
    "Through the Looking Glass",
    "Atlas Shrugged",
    "A House for Mr. Biswas",
    "The Heart Is A Lonely Hunter",
    "The Wind-Up Bird Chronicle",
    "The World According to Garp",
    "Wide Sargasso Sea",
    "The Voyage of the Dawn Treader: The Chronicles of Narnia",
    "I, Claudius",
    "Brave New World",
    "Jane Eyre",
    "The Man Without Qualities",
    "Women in Love",
    "The Corrections",
    "Lucky Jim",
    "Rabbit, Run",
    "Epic of Gilgamesh",
    "A Sentimental Education",
    "The Prime of Miss Jean Brodie",
    "Tess of the d'Urbervilles",
    "Possession",
    "The Complete Stories of Franz Kafka",
    "Look Homeward, Angel",
    "The Handmaid's Tale",
    "The Birds",
    "Fairy Tales and Stories",
    "Invisible Man",
    "Clarissa",
    "Le Morte d'Arthur",
    "Our Mutual Friend",
    "Faust",
    "Complete Poems of Giacomo Leopardi",
    "Animal Farm",
    "Treasure Island",
    "Wolf Hall",
    "Beloved",
    "The Persians",
    "A Prayer for Owen Meany",
    "Dubliners",
    "Antigone",
    "The Book of Disquiet",
    "Fathers and Sons",
    "The Idiot",
    "Middlesex",
    "Pedro Paramo",
    "The Road",
    "Les Misérables",
    "Oedipus the King",
    "Decameron",
    "The School for Wives",
    "Frankenstein",
    "My Antonia",
    "Selected Stories of Alice Munro",
    "The Sound and the Fury",
    "Madame Bovary",
    "The Bacchae",
    "All the King's Men",
    "Los Siete Locos",
    "White Teeth",
    "Medea",
    "Robinson Crusoe",
    "The Lord of the Rings",
    "The House of Mirth",
    "Sons and Lovers",
    "The Adventures of Augie March",
    "Lolita",
    "As I Lay Dying",
    "Catch-22",
    "Crime and Punishment",
    "Ulysses",
    "Metamorphoses",
    "Lord Jim",
    "In Search of Lost Time",
    "A Season in Hell",
    "The Last Battle: The Chronicles of Narnia",
    "Household Tales",
    "Nine Stories",
    "The Sonnets",
    "Gargantua and Pantagruel",
    "The Tale of Genji",
    "Molloy",
    "Of Human Bondage",
    "Prometheus Bound",
    "The Complete Poetry and Prose of William Blake",
    "The Complete Stories of Flannery O'Connor",
    "Cousin Bette",
    "Moll Flanders",
    "Lysistrata",
    "A Passage to India",
    "Waiting for Godot",
    "The Duino Elegies",
    "To the Lighthouse",
    "Little Women",
    "Dangerous Liaison",
    "David Copperfield",
    "Ajax",
    "The Stories of John Cheever",
    "The Complete Sherlock Holmes",
    "Electra",
    "The Red Badge of Courage",
    "Bleak House",
    "Moby Dick",
    "The Would-Be Gentleman",
    "The Three Musketeers",
    "Gone With the Wind",
    "Leaves of Grass",
    "The Leopard",
    "Their Eyes Were Watching God",
    "The Miser",
    "Mourning Becomes Electra",
    "The Big Sleep",
    "The Horse and His Boy: The Chronicles of Narnia",
    "Dead Souls",
    "Don Quixote",
    "Eugenie Grandet",
    "One Hundred Years of Solitude",
    "The Age of Innocence",
    "Nineteen Eighty Four",
    "The Poems of Robert Frost",
    "Stories of Ernest Hemingway",
    "Austerlitz",
    "Native Son",
    "Vanity Fair",
    "The House of the Spirits",
    "The Maltese Falcon",
    "The Clouds",
    "Pride and Prejudice",
    "The Unbearable Lightness of Being",
    "Journey to the End of The Night",
    "The Mill on the Floss",
    "The Killer Angels",
    "Mrs. Dalloway",
    "Collected Fiction",
    "Steppenwolf",
    "One Flew Over the Cuckoo's Nest",
    "The Misanthrope",
    "Pale Fire",
    "A Room With a View",
    "The Brief Wondrous Life of Oscar Wao",
    "The Pickwick Papers",
    "The Complete Tales and Poems of Edgar Allan Poe",
    "Lady Chatterley's Lover",
    "Hamlet",
    "The Magician's Nephew",
    "One Thousand and One Nights",
    "A Tale of Two Cities",
    "Henderson The Rain King",
    "The Princess of Cleves",
    "The Long Goodbye: A Novel",
    "The Sense of an Ending",
    "If on a Winter's Night a Traveller",
    "Herzog",
    "A Farewell to Arms",
    "The Grapes of Wrath",
    "A Clockwork Orange",
    "Macbeth",
    "The Charterhouse of Parma",
    "The Waste Land",
    "Alice's Adventures in Wonderland",
    "Harry Potter And The Philosopher's Stone",
    "To Kill a Mockingbird",
    "American Pastoral",
    "Of Mice and Men",
    "The Waves",
    "King Lear",
    "A Tree Grows in Brooklyn",
    "Poems of Emily Dickinson",
    "Blood Meridian",
    "Father Goriot",
    "Charlotte's Web",
    "The Trial",
    "Great Expectations",
    "The Count of Monte Cristo",
    "Bérénice",
    "Nineteen Nineteen",
    "Hunger",
    "The Hitchhiker's Guide to the Galaxy",
]

TABLE_NAMES = [ #? only works for values, so table names are hardcoded here, never user input
    "Roles",
    "FineRules",
    "Homerooms",
    "Users",
    "StudentProfiles",
    "Genres",
    "Authors",
    "Books",
    "BookAuthors",
    "BookCopies",
    "Loans"
]

def main():
    DB_PATH.unlink(missing_ok=True)

    init_db()
    con = get_connection()
    with con:
        role_ids = seed_roles(con)
        seed_fine_rules(con, role_ids)
        homeroom_names = seed_homerooms(con)
        user_ids = seed_users(con, role_ids)
        seed_student_profiles(con, user_ids["student"], homeroom_names)
        genre_ids = seed_genres(con)
        author_ids = seed_authors(con)
        book_ids = seed_books(con, genre_ids)
        seed_book_authors(con, book_ids, author_ids)
        copies_by_book = seed_book_copies(con, book_ids)

        today = date.today()
        seed_loans(con, user_ids, copies_by_book, today)
        seed_active_loans(con, user_ids, copies_by_book, today)

    print_row_counts(con)
    con.close()

def seed_roles(con):
    cur = con.cursor()
    roles = [(1, "student"), (2, "teacher"), (3, "librarian")]

    cur.executemany("INSERT INTO Roles (role_id, role_name) VALUES (?, ?)", roles)

    role_ids = {}
    for role_id, role_name in roles:
        role_ids[role_name] = role_id
    return role_ids

def seed_fine_rules(con, role_ids):
    cur = con.cursor()

    fine_rules = [(role_ids["student"], 3, 7, 0.50, 1.00, 20.00), (role_ids["teacher"], 2, 1, 0, 0.5, 50), (role_ids["librarian"], 1, 1, 0.5, 1, 50)] # !! placeholder values

    cur.executemany ("""INSERT INTO FineRules(role_id, grace_days, tier_1_days, tier_1_rate, tier_2_rate, max_amount) VALUES (?,?,?,?,?,?)""", fine_rules)

def seed_homerooms(con):
    cur = con.cursor()

    homeroom_rows = []
    homeroom_names = []

    for year in range(7, 14):
        homeroom = str(year)
        tutor_email = f"tutor.{homeroom}@bisc.krakow.pl"

        homeroom_rows.append((homeroom, tutor_email, year)) 
        homeroom_names.append(homeroom)

    cur.executemany("""INSERT INTO Homerooms (homeroom, tutor_email, year_number) VALUES (?,?,?)""", homeroom_rows)
    return homeroom_names

def seed_users(con, role_ids):
    cur = con.cursor()
 
    user_rows = []
    student_ids = []
    teacher_ids = []
    librarian_ids = []
 
    selected_names = random.sample(NAMES, 58)
 
    students = selected_names[:45]
    teachers = selected_names[45:52]
    librarians = selected_names[52:55]
 
    password_hash = bcrypt.hashpw(b"testpassword", bcrypt.gensalt()).decode() # shared password for all credentialised test accounts
 
    user_id = 0
 
    for first_name, last_name in students:
        user_id = user_id + 1
        email = f"{first_name.lower()}.{last_name.lower()}@bisc.krakow.pl"
 
        user_rows.append((user_id, role_ids["student"], email, 1, first_name, last_name, None, None))
        student_ids.append(user_id)
 
    for first_name, last_name in teachers: # 7 regular teachers
        user_id = user_id + 1
        email = f"{first_name.lower()}.{last_name.lower()}@bisc.krakow.pl"
 
        user_rows.append((user_id, role_ids["teacher"], email, 1, first_name, last_name, None, None))
        teacher_ids.append(user_id)

    librarian_number = 0

    for first_name, last_name in librarians: # 3 regular librarians
        librarian_number = librarian_number + 1
        user_id = user_id + 1
        email = f"{first_name.lower()}.{last_name.lower()}@bisc.krakow.pl"
        username = f"librarian{librarian_number}"

        user_rows.append((user_id, role_ids["librarian"], email, 1, first_name, last_name, username, password_hash))
        librarian_ids.append(user_id)

    first_name, last_name = selected_names[55] # inactive librarian must not be able to log in
    user_id = user_id + 1
    email = f"{first_name.lower()}.{last_name.lower()}@bisc.krakow.pl"
    user_rows.append((user_id, role_ids["librarian"], email, 0, first_name, last_name, "inactive_librarian", password_hash))

    first_name, last_name = selected_names[56] # teacher has credentials but must not be able to log in
    user_id = user_id + 1
    email = f"{first_name.lower()}.{last_name.lower()}@bisc.krakow.pl"
    user_rows.append((user_id, role_ids["teacher"], email, 1, first_name, last_name, "test_teacher", password_hash))

    first_name, last_name = selected_names[57] # inactive student
    user_id = user_id + 1
    email = f"{first_name.lower()}.{last_name.lower()}@bisc.krakow.pl"
    user_rows.append((user_id, role_ids["student"], email, 0, first_name, last_name, None, None))
    student_ids.append(user_id)
    inactive_student_id = user_id
 
    cur.executemany("""INSERT INTO Users (user_id, role_id, email, is_active, first_name, last_name, username, password_hash) VALUES (?,?,?,?,?,?,?,?)""", user_rows)
 
    return {"student": student_ids, "teacher": teacher_ids, "librarian": librarian_ids, "inactive_student": inactive_student_id}

def seed_student_profiles(con, student_ids, homeroom_names):
    cur = con.cursor()

    student_profiles = []

    for i in range(len(student_ids)): # spread evenly across homerooms
        user_id = student_ids[i]
        homeroom = homeroom_names[i % len(homeroom_names)]
        student_profiles.append((user_id, homeroom))

    cur.executemany("""INSERT INTO StudentProfiles(user_id, homeroom) VALUES (?, ?)""", student_profiles)

def seed_genres(con):
    cur = con.cursor()
 
    genres = [
        (1, "Fiction"),
        (2, "Science Fiction"),
        (3, "Fantasy"),
        (4, "Mystery"),
        (5, "Historical Fiction"),
        (6, "Biography"),
        (7, "History"),
        (8, "Science"),
        (9, "Poetry"),
        (10, "Contemporary"),
    ]

    cur.executemany("INSERT INTO Genres (genre_id, name) VALUES (?, ?)", genres)

    genre_ids = []
    for genre_id, genre_name in genres:
        genre_ids.append(genre_id)

    return genre_ids

def seed_authors(con):
    cur = con.cursor()
 
    author_rows = []
    author_ids = []
 
    selected_names = random.sample(NAMES, 30)
 
    for i in range(len(selected_names)):
        author_id = i + 1
        first_name, last_name = selected_names[i]
 
        author_rows.append((author_id, first_name, last_name))
        author_ids.append(author_id)
 
    cur.executemany("""INSERT INTO Authors (author_id, first_name, last_name) VALUES (?,?,?)""", author_rows)
    return author_ids

def seed_books(con, genre_ids):
    cur = con.cursor()
 
    book_rows = []
    book_ids = []
 
    for i in range(len(TITLES)):
        book_id = i + 1
        title = TITLES[i]
        isbn = "978" + str(book_id).zfill(10) # unique isbn values, fills string with 0's
        publication_year = random.randint(1950, 2024)
        publisher = random.choice(PUBLISHERS)
        genre_id = random.choice(genre_ids)
 
        book_rows.append((book_id, isbn, title, publication_year, publisher, genre_id))
        book_ids.append(book_id)
 
    cur.executemany("""INSERT INTO Books (book_id, isbn, title, publication_year, publisher, genre_id) VALUES (?,?,?,?,?,?)""", book_rows)
    return book_ids

def seed_book_authors(con, book_ids, author_ids):
    cur = con.cursor()
 
    book_author_rows = []
 
    for book_id in book_ids: 
        author_id = random.choice(author_ids)
        book_author_rows.append((book_id, author_id))
 
    cur.executemany("""INSERT INTO BookAuthors (book_id, author_id) VALUES (?, ?)""", book_author_rows)

def seed_book_copies(con, book_ids):
    cur = con.cursor()
 
    copies_by_book = {}
 
    for book_id in book_ids: # three physical copies of every book
        copies_by_book[book_id] = []

        for copy_number in range(1, 4):
            cur.execute("INSERT INTO BookCopies (book_id) VALUES (?)", (book_id,))
            copy_id = cur.lastrowid
            copies_by_book[book_id].append(copy_id)

    return copies_by_book

def seed_loans(con, user_ids, copies_by_book, today):
    cur = con.cursor()

    borrowers = []

    for user_id in user_ids["student"][:-5]: # last 5 students
        borrowers.append((user_id, Student.MAX_LOAN_DAYS))
 
    for user_id in user_ids["teacher"][:-1]:
        borrowers.append((user_id, Teacher.MAX_LOAN_DAYS))

    loan_rows = []
    year_start = today - timedelta(days=365)
    stop_date = today - timedelta(days=60) 

    for book_id in copies_by_book:
        if book_id <= 40: #first 40 titles are the popular ones
            loans_per_copy = 3
        else:
            loans_per_copy = 1

        for copy_id in copies_by_book[book_id]:
            next_free = year_start

            for loan_number in range(loans_per_copy):
                checkout = next_free + timedelta(days=random.randint(1, 10)) 
                user_id, max_loan_days = random.choice(borrowers)
                due = checkout + timedelta(days=max_loan_days)
                returned = due + timedelta(days=random.randint(-10, 5))

                if returned < checkout:
                    returned = checkout

                if returned > stop_date:
                    break

                loan_rows.append((copy_id, user_id, checkout.isoformat(), due.isoformat(), returned.isoformat(), "returned"))
                next_free = returned + timedelta(days=1) # this stops two loans overlapping on one copy

    cur.executemany("""INSERT INTO Loans (copy_id, user_id, checkout_date, due_date, return_date, status) VALUES (?,?,?,?,?,?)""", loan_rows)

def seed_active_loans(con, user_ids, copies_by_book, today):
    cur = con.cursor()

    borrowers = []

    for user_id in user_ids["student"][:-5]:
        borrowers.append((user_id, Student.MAX_LOAN_DAYS))

    for user_id in user_ids["teacher"][:-1]:
        borrowers.append((user_id, Teacher.MAX_LOAN_DAYS))

    available_copies = []

    for copy_ids in copies_by_book.values():
        for copy_id in copy_ids:
            available_copies.append(copy_id)

    random.shuffle(available_copies)

    loan_rows = []
    loaned_copy_ids = []

    for loan_number in range(44):
        copy_id = available_copies.pop()
        user_id, max_loan_days = random.choice(borrowers)

        checkout = today - timedelta(days=random.randint(1, max_loan_days - 1))
        due = checkout + timedelta(days=max_loan_days)

        loan_rows.append((copy_id, user_id, checkout.isoformat(), due.isoformat(), None, "active"))
        loaned_copy_ids.append((copy_id,))

    copy_id = available_copies.pop()
    user_id, max_loan_days = random.choice(borrowers)

    checkout = today - timedelta(days=max_loan_days)
    due = checkout + timedelta(days=max_loan_days)

    loan_rows.append((copy_id, user_id, checkout.isoformat(), due.isoformat(), None, "active"))
    loaned_copy_ids.append((copy_id,))

    for loan_number in range(14):
        copy_id = available_copies.pop()
        user_id, max_loan_days = random.choice(borrowers)

        checkout = today - timedelta(days=max_loan_days + random.randint(2, 30))
        due = checkout + timedelta(days=max_loan_days)

        loan_rows.append((copy_id, user_id, checkout.isoformat(), due.isoformat(), None, "active"))
        loaned_copy_ids.append((copy_id,))

    copy_id = available_copies.pop()
    user_id, max_loan_days = random.choice(borrowers)

    checkout = today - timedelta(days=max_loan_days + 1)
    due = checkout + timedelta(days=max_loan_days)

    loan_rows.append((copy_id, user_id, checkout.isoformat(), due.isoformat(), None, "active"))
    loaned_copy_ids.append((copy_id,))

    cur.executemany("""INSERT INTO Loans (copy_id, user_id, checkout_date, due_date, return_date, status) VALUES (?,?,?,?,?,?)""", loan_rows)
    cur.executemany("""UPDATE BookCopies SET status = 'loaned' WHERE copy_id = ?""", loaned_copy_ids)



def print_row_counts(con):
    cur = con.cursor()
 
    print("Seeding summary:")
 
    for table_name in TABLE_NAMES:
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cur.fetchone()[0]
        print(f"- {table_name}: {row_count}")

    
if __name__ == "__main__":
    main()