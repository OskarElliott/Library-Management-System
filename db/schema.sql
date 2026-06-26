PRAGMA foreign_keys = ON;

CREATE TABLE Roles (
    role_id     INTEGER PRIMARY KEY,
    role_name   TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE Users (
    user_id         INTEGER PRIMARY KEY,
    username        TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    role_id         INTEGER NOT NULL REFERENCES Roles(role_id),
    email           TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active       INTEGER NOT NULL DEFAULT 1 -- sqlite has no booleans
);

CREATE TABLE StudentProfiles (
    user_id             INTEGER PRIMARY KEY REFERENCES Users(user_id),
    year_number         INTEGER NOT NULL CHECK(year_number BETWEEN 7 and 13), -- ib1 / ib2 stored as years 12 and 13
    homeroom            TEXT,
    form_tutor_email    TEXT
);

CREATE TABLE Publishers (
    publisher_id    INTEGER PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    country         TEXT
);

CREATE TABLE Genres (
    genre_id        INTEGER PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE
);

CREATE TABLE Authors (
    author_id   INTEGER PRIMARY KEY,
    first_name  TEXT,
    last_name   TEXT NOT NULL
);

CREATE TABLE Books (
    book_id             INTEGER PRIMARY KEY,
    isbn                TEXT NOT NULL UNIQUE,
    title               TEXT NOT NULL,
    publication_year    INTEGER,
    publisher_id        INTEGER REFERENCES Publishers(publisher_id),
    genre_id            INTEGER REFERENCES Genres(genre_id),
    description         TEXT,
    replacement_cost    REAL NOT NULL DEFAULT 0 
);

CREATE TABLE BookAuthors (
    book_id     INTEGER NOT NULL REFERENCES Books(book_id),
    author_id   INTEGER NOT NULL REFERENCES Authors(author_id),
    PRIMARY KEY (book_id, author_id)   
);

CREATE TABLE BookCopies (
    copy_id         INTEGER PRIMARY KEY,
    book_id         INTEGER NOT NULL REFERENCES Books(book_id),
    purchase_date   TEXT,
    condition       TEXT,
    status          TEXT NOT NULL DEFAULT 'available'
        CHECK (status IN ('available','loaned','reserved','lost','discarded'))
);

CREATE TABLE Loans (
    loan_id         INTEGER PRIMARY KEY,
    copy_id         INTEGER NOT NULL REFERENCES BookCopies(copy_id),
    user_id         INTEGER NOT NULL REFERENCES Users(user_id),
    checkout_date   TEXT NOT NULL,
    due_date        TEXT NOT NULL,
    return_date     TEXT, --is null while on loan
    status          TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN('active', 'returned', 'lost'))
);

CREATE TABLE Reservations (
    reservation_id      INTEGER PRIMARY KEY,
    book_id             INTEGER NOT NULL REFERENCES Books(book_id),
    user_id             INTEGER NOT NULL REFERENCES Users(user_id),
    request_date        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    priority            INTEGER NOT NULL,
    status              TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'ready', 'fulfilled', 'expired', 'cancelled')),
    notified_date       TEXT, -- set when ready email is sent
    expires_at          TEXT -- ready time + 48h
);

CREATE TABLE FineRules (
    rule_id     INTEGER PRIMARY KEY,
    role_id     INTEGER NOT NULL UNIQUE REFERENCES Roles(role_id),
    grace_days  INTEGER NOT NULL DEFAULT 0,
    tier_1_rate REAL NOT NULL, -- daily rate after grace period
    tier_2_rate REAL NOT NULL, -- escalated daily rate
    max_amount  REAL NOT NULL 
);

CREATE TABLE Fines (
    fine_id     INTEGER PRIMARY KEY,
    loan_id     INTEGER NOT NULL REFERENCES Loans(loan_id),
    amount      REAL NOT NULL,
    issued_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    paid_date   TEXT, -- null while unpaid
    status      TEXT NOT NULL DEFAULT 'unpaid'
        CHECK (status IN ('unpaid', 'paid', 'cancelled'))
);

CREATE TABLE SchoolCalendar (
    day_date    TEXT PRIMARY KEY, -- iso yyyy-mm-dd
    is_open     INTEGER NOT NULL DEFAULT 1,
    day_type    TEXT NOT NULL
        CHECK (day_type IN ('school_day', 'weekend', 'holiday')),
    notes       TEXT
);

CREATE TABLE Notifications (
    notification_id     INTEGER PRIMARY KEY,
    loan_id             INTEGER REFERENCES Loans(loan_id),
    recipient_id        INTEGER NOT NULL REFERENCES Users(user_id),
    notification_type   TEXT NOT NULL
        CHECK (notification_type IN ('overdue_warning', 'alert', 'reservation_ready')),
    recipient_email     TEXT NOT NULL,
    sent_at             TEXT,
    status              TEXT NOT NULL DEFAULT 'sent'
        CHECK (status IN ('sent', 'failed', 'undelivered'))
);

CREATE TABLE AuditLog (
    log_id      INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES Users(user_id),
    action      TEXT NOT NULL,
    table_name  TEXT,
    record_id   INTEGER,
    logged_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE VIEW borrowing_eligibility AS
SELECT
    u.user_id,
    u.username,
    COUNT(DISTINCT CASE WHEN l.status = 'active' THEN l.loan_id END) AS active_loans,
    COALESCE(SUM(CASE WHEN f.status = 'unpaid' THEN f.amount ELSE 0 END), 0) AS outstanding_fines
FROM Users u
LEFT JOIN Loans l ON l.user_id = u.user_id
LEFT JOIN Fines f ON f.loan_id = l.loan_id
GROUP BY u.user_id, u.username;
