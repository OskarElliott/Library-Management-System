PRAGMA foreign_keys = ON;

CREATE TABLE Roles (
    role_id INTEGER PRIMARY KEY,
    role_name TEXT NOT NULL
);

CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY,
    role_id INTEGER REFERENCES Roles(role_id) NOT NULL,
    email TEXT UNIQUE, 
    is_active INTEGER NOT NULL DEFAULT 1 -- active by default
        CHECK (is_active IN(0,1)),
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    username TEXT UNIQUE, -- staff only
    password_hash TEXT -- staff only
    CHECK ((username IS NULL AND password_hash IS NULL) OR (username IS NOT NULL AND password_hash IS NOT NULL))
);

CREATE TABLE Homerooms (
    homeroom TEXT PRIMARY KEY,
    tutor_email TEXT NOT NULL
);

CREATE TABLE StudentProfiles (
    user_id INTEGER PRIMARY KEY REFERENCES Users(user_id),
    year_number INTEGER NOT NULL CHECK(year_number BETWEEN 7 AND 13), -- ib1 and ib2 marked as years 12 and 13.
    homeroom TEXT NOT NULL REFERENCES Homerooms(homeroom)
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

CREATE TABLE BookAuthors ( -- junction table for many:many relationship
    book_id INTEGER NOT NULL REFERENCES Books(book_id),
    author_id INTEGER NOT NULL REFERENCES Authors(author_id),
    PRIMARY KEY (book_id, author_id)
);

CREATE TABLE Loans (
    loan_id INTEGER PRIMARY KEY,
    copy_id INTEGER NOT NULL REFERENCES BookCopies(copy_id),
    user_id INTEGER NOT NULL REFERENCES Users(user_id),
    checkout_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date TEXT NOT NULL,
    return_date TEXT,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active','returned','lost'))
    CHECK ((status = 'active' AND return_date IS NULL) OR (status = 'returned' AND return_date IS NOT NULL) OR (status = 'lost'))
);

CREATE TABLE Reservations (
    reservation_id INTEGER PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES Books(book_id),
    user_id INTEGER NOT NULL REFERENCES Users(user_id),
    request_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'waiting'
        CHECK (status IN ('waiting','ready for pickup','collected','cancelled'))
);

CREATE TABLE Fines (
    fine_id INTEGER PRIMARY KEY,
    loan_id INTEGER NOT NULL REFERENCES Loans(loan_id),
    amount REAL NOT NULL
        CHECK (amount >= 0),
    issued_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    paid_date TEXT,
    status TEXT NOT NULL DEFAULT 'unpaid'
        CHECK (status IN ('unpaid','paid'))
    CHECK ((status = 'unpaid' AND paid_date IS NULL) OR (status = 'paid' AND paid_date IS NOT NULL))
);

CREATE TABLE FineRules (
    role_id INTEGER PRIMARY KEY REFERENCES Roles(role_id), -- pk enforces 1 fine per role, fk links the rule to roles
    grace_days INTEGER NOT NULL CHECK (grace_days >= 0 ),
    tier_1_days INTEGER NOT NULL CHECK (tier_1_days >= 1),
    tier_1_rate REAL NOT NULL CHECK (tier_1_rate >= 0),
    tier_2_rate REAL NOT NULL CHECK (tier_2_rate >= 0),
    max_amount REAL NOT NULL CHECK (max_amount >= 0) 
);

CREATE TABLE ClosedDays (
    day_date TEXT PRIMARY KEY -- only for non-weekend closures, weekends are computed
);

CREATE TABLE AuditLog (
    log_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES Users(user_id),
    action TEXT NOT NULL,
    table_name TEXT,
    record_id INTEGER,
    logged_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Notifications (
    notification_id INTEGER PRIMARY KEY,
    loan_id INTEGER REFERENCES Loans(loan_id), 
    user_id INTEGER NOT NULL REFERENCES Users(user_id),
    type TEXT NOT NULL
        CHECK (type IN('reservation ready','due soon','overdue','fine issued')),
    sent_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE VIEW BorrowingEligibility AS 
SELECT Users.user_id,
    COUNT (DISTINCT CASE WHEN Loans.status = 'active' THEN Loans.loan_id END) AS active_loans,
    COALESCE(SUM (CASE WHEN fines.status = 'unpaid' THEN fines.amount END), 0) AS outstanding_fines 
FROM Users
LEFT JOIN Loans ON Loans.user_id = Users.user_id
LEFT JOIN Fines ON Fines.loan_id = Loans.loan_id
GROUP BY Users.user_id;
