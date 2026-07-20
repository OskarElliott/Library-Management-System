PRAGMA foreign_keys = ON;

CREATE TABLE Roles (
    role_id INTEGER PRIMARY KEY,
    role_name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role_id INTEGER REFERENCES Roles(role_id) NOT NULL,
    email TEXT UNIQUE, -- email required for student to activate email notifications
    created_at TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1 -- active by default
);

CREATE TABLE StudentProfiles (
    user_id INTEGER PRIMARY KEY REFERENCES Users(user_id),
    year_number INTEGER NOT NULL CHECK(year_number BETWEEN 7 AND 13), -- ib1 and ib2 marked as years 12 and 13. No student profiles for primary students
    homeroom TEXT NOT NULL,
    form_tutor_email TEXT NOT NULL
);

CREATE TABLE Genres (
    genre_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE Authors (
    author_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT NOT NULL
);

CREATE TABLE Books (
    book_id INTEGER PRIMARY KEY,
    isbn TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    publication_year INTEGER,
    publisher TEXT,
    genre_id INTEGER NOT NULL REFERENCES Genres(genre_id),
    replacement_cost REAL
);

CREATE TABLE BookCopies (
    copy_id INTEGER PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES Books(book_id),
    purchase_date TEXT,
    condition TEXT NOT NULL DEFAULT 'new'
        CHECK(condition IN('new','good','fair','damaged')),
    status TEXT NOT NULL DEFAULT 'available'
        CHECK(status IN('available','loaned','reserved','lost','discarded'))
);

CREATE TABLE BookAuthors