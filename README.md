# Library Management System

School library management system built as an IB Computer Science SL Internal Assessment (2027 session). 

## Stack

- Python 3.13
- PySide6 (desktop UI)
- SQLite via the standard library `sqlite3` (no ORM)
- bcrypt for password hashing
- Parameterised SQL everywhere

## Scope

Role-based login (student,teacher, librarian), book and copy management, borrow and return, and overdue detection computed from due dates. Additions, added only if time allows: fines, Google Books lookup, demand analytics, email notifications, and reservations.
