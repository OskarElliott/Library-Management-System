# wipes and reseeds library.db with synthetic test data
import random
import bcrypt
from db.connection import init_db, get_connection, DB_PATH

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

ROW_COUNT_QUERIES = [ # table names cannot be parameterised, so each query is written out in full
    ("Roles", "SELECT COUNT(*) FROM Roles"),
    ("FineRules", "SELECT COUNT(*) FROM FineRules"),
    ("Homerooms", "SELECT COUNT(*) FROM Homerooms"),
    ("Users", "SELECT COUNT(*) FROM Users"),
    ("StudentProfiles", "SELECT COUNT(*) FROM StudentProfiles"),
    ("Genres", "SELECT COUNT(*) FROM Genres"),
    ("Authors", "SELECT COUNT(*) FROM Authors"),
    ("Books", "SELECT COUNT(*) FROM Books"),
    ("BookAuthors", "SELECT COUNT(*) FROM BookAuthors"),
    ("BookCopies", "SELECT COUNT(*) FROM BookCopies"),
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
        seed_book_copies(con, book_ids)

    print_row_counts(con)
    con.close()

def seed_roles(con):
    cur = con.cursor()
    roles = [(1, "student"), (2, "teacher"), (3, "librarian")]

    cur.executemany("INSERT INTO Roles (role_id, role_name) VALUES (?, ?)", roles)

    return {
        role_name: role_id
        for role_id, role_name in roles
    }

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

    student_ids = []
    teacher_ids = []
    librarian_ids = []

    selected_names = random.sample(NAMES, 55)

    students = selected_names[:45]
    teachers = selected_names[45:52]
    librarians = selected_names[52:]

    for first_name, last_name in students:
        email = f"{first_name.lower()}.{last_name.lower()}@bisc.krakow.pl"

        cur.execute ("""INSERT INTO Users (role_id, email, first_name, last_name, username, password_hash) VALUES (?,?,?,?,?,?)""", (role_ids["student"], email, first_name, last_name, None, None))
        student_ids.append(cur.lastrowid)
        
    for first_name, last_name in teachers:
        email = f"{first_name.lower()}.{last_name.lower()}@bisc.krakow.pl"
    
        cur.execute ("""INSERT INTO Users (role_id, email, first_name, last_name, username, password_hash) VALUES (?,?,?,?,?,?)""", (role_ids["teacher"], email, first_name, last_name, None, None))
        teacher_ids.append(cur.lastrowid)

    password_hash = bcrypt.hashpw(b"testpassword", bcrypt.gensalt()).decode() # shared password for all librarian accounts

    for first_name, last_name in librarians:
        email = f"{first_name.lower()}.{last_name.lower()}@bisc.krakow.pl"
        username = f"{first_name.lower()}"

        cur.execute ("""INSERT INTO Users (role_id, email, first_name, last_name, username, password_hash) VALUES (?,?,?,?,?,?)""", (role_ids["librarian"], email, first_name, last_name, username, password_hash))
        librarian_ids.append(cur.lastrowid)

    return {"student": student_ids, "teacher": teacher_ids, "librarian": librarian_ids}

def seed_student_profiles(con, student_ids, homeroom_names):
    cur = con.cursor()

    student_profiles = []

    for i in range(len(student_ids)): # distribute 45 test students evenly across 7 homerooms
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
        isbn = f"978{book_id:010d}" # unique isbn values
        publication_year = random.randint(1950, 2024)
        publisher = random.choice(PUBLISHERS)
        genre_id = random.choice(genre_ids)
        replacement_cost = round(random.uniform(20, 120), 2)
 
        book_rows.append((book_id, isbn, title, publication_year, publisher, genre_id, replacement_cost))
        book_ids.append(book_id)
 
    cur.executemany("""INSERT INTO Books (book_id, isbn, title, publication_year, publisher, genre_id, replacement_cost) VALUES (?,?,?,?,?,?,?)""", book_rows)
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
 
    copy_rows = []
 
    for book_id in book_ids: # three physical copies of every book
        for copy_number in range(1, 4):
            copy_rows.append((book_id,))
 
    cur.executemany("INSERT INTO BookCopies (book_id) VALUES (?)", copy_rows)

def print_row_counts(con):
    cur = con.cursor()
 
    print("Seeding summary:")
 
    for table_name, count_query in ROW_COUNT_QUERIES:
        cur.execute(count_query)
        row_count = cur.fetchone()[0]
        print(f"  {table_name}: {row_count}")

    
if __name__ == "__main__":
    main()