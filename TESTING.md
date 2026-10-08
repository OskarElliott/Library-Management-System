# testing log

the single record of every test run against the library management system.
feeds criterion c4 (the strategy, without results) and criterion d4 (the same
tests with results and video timestamps).

organised by success criterion, not by build phase, because the ib says to
structure criterion d with subheadings based on the success criteria rather than
as a narrative of how the product was built.

test ids are permanent. once a test has an id it keeps it forever, even if the
test is rewritten, because criterion d refers back to criterion c by number to
save word count.

**rule: no result goes in this file unless it was read back from the database or
seen on screen.** "no exception was raised" is not a result. a row marked
"pass (screen only)" was seen on screen but has no screenshot yet; get one
before the video.

last updated: 2026-10-08 (phase 5 build complete).

---

## how to record a test

| column | what goes in it |
|---|---|
| id | F1.1, S3.2 etc. F = functional, S = structural, X = system-level. the number after the letter is the success criterion. |
| input | the exact values typed, not a description. "title blank, isbn 9780000000250" not "invalid input" |
| expected | what should happen, including what the database should look like afterwards |
| actual | what happened, with the ids involved and the query output pasted in |
| date | when it was run, and which machine |
| video | timestamp, filled in at phase 12 |
| status | pass / fail / not run |

always write down the book_id, copy_id or loan_id **before** acting, then query
that id. three times so far a result looked like a failure because the wrong
record was queried afterwards.

`row_factory` is set to `sqlite3.Row` in connection.py, so a fetch prints as
`<sqlite3.Row object>` and hides every value. wrap it to paste a real result:
`[tuple(row) for row in cur.fetchall()]`, or `cur.fetchone()[0]` for a count.

from phase 5 the seeded dates are **relative to the day the seeder ran**, so a
result is only meaningful against its date column. expectations are written
relatively ("due today is not overdue"), never as fixed dates. reseed before any
testing session: a database left from a previous week reports a different
overdue count for the same code.

### repl setup used from phase 5

paste at the `>>>` prompt (not powershell), with no leading spaces, in every new
session. use `get_connection()`, never `sqlite3.connect("library.db")`: a
relative path run from another folder silently creates a new empty database.

```python
from datetime import date, timedelta
from db.connection import get_connection
from services import books, loans
con = get_connection()
cur = con.cursor()
today = date.today().isoformat()

def show(sql, params=()):
    cur.execute(sql, params)
    print([tuple(row) for row in cur.fetchall()])

def attempt(function, *args):
    try:
        print("returned:", function(*args))
    except ValueError as error:
        print("ValueError:", error)
```

`attempt` prints a ValueError instead of stopping the pasted block, so the
after-state checks below a refusal still run. the 3.13 repl runs a pasted block
as one unit and stops at the first exception, which is why several 2026-10-04
after-state checks never printed the first time.

---

## sc1 — staff login (functional)

| id | input | expected | actual | date | video | status |
|---|---|---|---|---|---|---|
| F1.1 | `librarian1` / `testpassword` | login succeeds, main window opens with the correct first name | main window opened, greeting showed the correct name. re-run after the seeder changed how librarian usernames are made | 2026-09-28 mac | | pass |
| F1.2 | valid username, wrong password | generic error, dialog stays open | "Invalid username or password" | 2026-07-31 win | | pass |
| F1.3 | username that does not exist | same generic error | | | | not run |
| F1.4 | username blank / password blank | presence check fires before any query | "Please enter a username and password" | 2026-07-31 win | | pass |
| F1.5 | `inactive_librarian` / `testpassword` (is_active = 0) | login refused with the same generic error as a wrong password; the `is_active = 1` clause is what stops it, not bcrypt | refused, "Invalid username or password" | 2026-09-28 mac | | pass |
| F1.6 | `test_teacher` / `testpassword` (teacher row with valid credentials) | login refused; the `role_name = 'librarian'` clause is what stops it, since the Users CHECK permits a credentialed teacher | refused, "Invalid username or password" | 2026-09-28 mac | | pass |
| F1.7 | `auth.login("librarian1", "testpassword")` timed with `time.perf_counter()` over 10 runs on the test machine | median and max both < 1 s (sc1 target, see appendix A); record both plus the machine. the single 0.22 s run on 2026-09-29 is superseded | | | | not run |

F1.5 and F1.6 were blocked from phase 2 until 2026-09-28, when the two fixtures
were added to the seeder. both accounts hold a valid bcrypt hash, so bcrypt
verifies them happily; only the login query's two extra clauses refuse them, and
until this date neither clause had ever executed.

## sc1 — login (structural)

| id | input | expected | actual | date | video | status |
|---|---|---|---|---|---|---|
| S1.1 | username `' OR '1'='1` | parameterised query treats it as a literal string, login fails. **this is now the main parameterisation evidence for sc2**, since the issue loan title filter runs in python and catalogue search was dropped | | | | not run |
| S1.2 | username with leading/trailing spaces | stripped before the query | | | | not run |
| S1.3 | password with leading/trailing spaces | **not** stripped, spaces are valid password characters | | | | not run |

---

## sc2 — audit log

| id | input | expected | actual | date | video | status |
|---|---|---|---|---|---|---|
| F2.1 | add a book | exactly one AuditLog row, action add_book, table_name Books, correct user_id | log 6: `(6, 53, 'add_book', 'Books', 202, '2026-08-10 11:10:51')` — one row covering the book, the author lookup and the BookAuthors link | 2026-08-10 win | | pass |
| F2.2 | add a copy | one row, table_name BookCopies, record_id = copy_id | `('add_copy', 'BookCopies', 604)` | 2026-09-11 win | | pass |
| F2.3 | discard a copy | one row, table_name BookCopies | `('discard_copy', 'BookCopies', 532)`; re-run `(2, 53, 'discard_copy', 'BookCopies', 10, …)` | 2026-09-11 win, 2026-10-04 win | | pass |
| F2.4 | withdraw a book | one row only, not one per copy discarded | `('withdraw_book', 'Books', 201)` — single row for an operation touching 3 rows across 2 tables; re-run `(1, 53, 'withdraw_book', 'Books', 3, …)` | 2026-09-11 win, 2026-10-04 win | | pass |
| F2.5 | log out, log in as a different librarian, then write something | the two most recent AuditLog rows carry two different user_ids | | | | not run |
| F2.6 | issue a loan | one row, action issue_loan, table_name Loans, record_id = loan_id, user_id = the logged-in librarian | `(1, 53, 'issue_loan', 'Loans', 907)`. through the ui: three rows `(1, 53, 'issue_loan', 'Loans', 907)`, `(2, … 908)`, `(3, … 909)` | 2026-10-04 win, 2026-10-08 win | | pass |
| F2.7 | three failed loan attempts in a row | no audit rows written for attempts that raised | `COUNT(*) FROM AuditLog` still 1 after three ValueErrors | 2026-10-04 win | | pass |
| F2.8 | return_loan, mark_lost and discard_copy in one sequence | one audit row per action, in order | `[('issue_loan', 907), ('return_loan', 907), ('issue_loan', 908), ('mark_lost', 908), ('discard_copy', 16), ('return_loan', 908)]` | 2026-10-08 win | | pass |
| F2.9 | four refused or cancelled ui actions (S3.9, S3.9b, S3.15 ui, S3.16 ui) on a fresh reseed | no audit rows at all | `[]` | 2026-10-04 win | | pass |
| S2.1 | add_book with user_id 99999 | FK on AuditLog.user_id fails, the whole transaction rolls back, no book inserted | `FOREIGN KEY constraint failed`, book not inserted. also proves `PRAGMA foreign_keys = ON` is applied per connection | 2026-08-05 win | | pass |
| S2.2 | return_loan crashing between its first and second UPDATE (the missing-tuple-comma bug, see failures) | the Loans update already ran is rolled back by `with con:`; nothing from the return reaches the database | loan `(907, 'active', None)`, copy `(13, 'loaned')`, audit only `[('issue_loan', 907)]` | 2026-10-08 win | | pass |

S2.2 was not planned. it is the transaction design proven by a real failure:
the loan update executed, the copy update raised `ProgrammingError`, and the
database ended exactly as it was before the return.

---

## sc3 — book and copy management

### functional

| id | input | expected | actual | date | video | status |
|---|---|---|---|---|---|---|
| F3.1 | add a book, all fields, 2 copies | Books row, Authors row, BookAuthors link, 2 BookCopies rows | book 202, copies 602 + 603, `COUNT(*) = 2` | 2026-08-10 win | | pass |
| F3.2 | add a book, required fields only | publisher and year stored as NULL, not "" | `(201, '9780000000250', 'Test Book', None, None, 1, 1)` | 2026-08-10 win | | pass |
| F3.3 | edit a book's title | change persisted, main table shows it after reload | audit logs 9 and 10, edit_book on Books 201 and 202 | 2026-08-10 win | | pass |
| F3.4 | withdraw a book | is_active = 0, row still present, every copy discarded, gone from the catalogue list | book 202 → `(202, 'Test Book v2', 0)`, copies `[(602,'discarded'),(603,'discarded')]` | 2026-08-10 win | | pass |
| F3.4r | regression after the withdraw guard was added: withdraw book 3 (no loaned copies) | same as F3.4, one audit row | book `(3, 0)`; copies `[(7,'discarded'),(8,'discarded'),(9,'discarded')]`; `(1, 53, 'withdraw_book', 'Books', 3, …)` | 2026-10-04 win | | pass |
| F3.5 | add a copy from the edit dialog | new BookCopies row appears in the dialog table immediately | copy 604 added to book 178, status available | 2026-09-11 win | | pass |
| F3.6 | discard a copy | selected copy status → discarded, row still present, other copies untouched | book 178 → `[(532,'discarded'),(533,'available'),(534,'available'),(604,'available')]` | 2026-09-11 win | | pass |
| F3.6r | regression after discard_copy was restructured: discard copy 10 (available) | only copy 10 discarded, one audit row | `[(10,'discarded'),(11,'available'),(12,'available')]`; `(2, 53, 'discard_copy', 'BookCopies', 10, …)` | 2026-10-04 win | | pass |

### structural — valid, extreme, invalid

| id | input | expected | actual | date | video | status |
|---|---|---|---|---|---|---|
| S3.1 | title blank | ValueError, message in the dialog, nothing written | "Title is required" | 2026-08-10 win | | pass |
| S3.2 | isbn already in Books | "A book with this ISBN already exists" (message changed 2026-10-05 to match the wireframe), no partial write | original run: "ISBN already exists", `COUNT(*)` still 202. re-run with the new message: isbn `9780000000001` → "A book with this ISBN already exists" | 2026-08-10 win, 2026-10-06 win | | pass (re-run screen only) |
| S3.3 | genre left on `-- Select Genre --` | ValueError, the placeholder carries None | "Genre is required" | 2026-08-10 win | | pass |
| S3.4 | publication year `abc` | type check, ValueError | "Publication year must be a number" | 2026-08-10 win | | pass |
| S3.5 | publication year `0` | range check, ValueError | "Publication year is out of range" | 2026-08-10 win | | pass |
| S3.6 | publication year `1000` and `2100` | boundary values, both accepted | | | | not run |
| S3.7 | publication year `999` and `2101` | just outside the boundary, both rejected | | | | not run |
| S3.8 | discard a copy that is already discarded | ValueError "Copy is already discarded.", no audit row | discard copy 10 twice: `ValueError: Copy is already discarded.`; AuditLog count 2 before and after | 2026-10-04 win | | pass |
| S3.9 | click empty space in the copies table (table has focus, no row highlighted), then Discard Copy | "Select a copy to discard.", nothing written | message shown; copy 1 still available. **before the fix this exact sequence discarded copy 1** (see failures) | 2026-10-04 win | | pass |
| S3.9b | highlight copy 1, Discard Copy, press Enter on the confirmation | confirmation reads "Discard copy 1?", No has focus, Enter writes nothing | screenshot: "Discard copy 1? This cannot be undone." with No focused; copy 1 still `available` | 2026-10-04 win | | pass |
| S3.10 | author name that already exists | existing author_id reused, no second Authors row | | | | not run |
| S3.11 | author with no first name | `first_name IS ?` matches NULL correctly, no duplicate inserted | | | | not run |
| S3.12 | author name containing an apostrophe (O'Donnell) | parameterised query stores and reads it back intact | | | | not run |
| S3.13 | isbn of a **withdrawn** title | duplicate error with no route forward — known limitation, no reinstate workflow | | | | not run |
| S3.14 | fields containing only spaces | stripped in the service, treated as empty, ValueError | | | | not run |
| S3.15 | discard a copy whose status is 'loaned' (copy 3, book 1) | refused, ValueError, copy unchanged | repl: `ValueError: Copy is on loan, it must be returned before discarding.`; copy `(3, 'loaned')`; AuditLog 0. ui: confirmation read "Discard copy 3?", Yes → same message in the dialog label | 2026-10-04 win | | pass |
| S3.16 | withdraw a title that has a copy on loan (book 1) | refused, no copies discarded, title still active | repl: `ValueError: Copies on loan: 1. Return them before withdrawing.`; book `(1, 1)`; copies `[(1,'available'),(2,'available'),(3,'loaned')]` before and after; AuditLog 0. ui: Enter on the confirmation did nothing; Yes → same message | 2026-10-04 win | | pass |
| S3.17 | `get_available_copies(1)` next to `get_copies(1)`, copy 3 on loan | the loaned copy is listed by get_copies only | `[(1, None, 'new', 'available'), (2, None, 'new', 'available'), (3, None, 'new', 'loaned')]` vs `[(1, 'new'), (2, 'new')]` | 2026-10-04 win | | pass |

---

## sc4 — borrowing and returns

strategy written 2026-09-12, before `services/loans.py` existed. service layer
built and tested 2026-09-28 to 2026-10-04; issue loan dialog 2026-10-05 to
2026-10-08; return and mark lost buttons 2026-10-08.

### functional — service

| id | input | expected | actual | date | video | status |
|---|---|---|---|---|---|---|
| F4.1 | `issue_loan(copy_id 1, user 42, librarian 53, today)` | one Loans row status active, checkout_date today, due_date = today + `Student.MAX_LOAN_DAYS`, copy now 'loaned', one AuditLog row | loan 907: `(907, 1, 42, '2026-10-04', '2026-10-18', None, 'active')`; copy `(1, 'loaned')`; audit `(1, 53, 'issue_loan', 'Loans', 907)`. after issue_loan began returning the due date: `(907, '2026-10-18')`. regression after the try/finally restructure: `(907, '2026-10-22')` | 2026-10-04 win, 2026-10-08 win | | pass |
| F4.2 | issue a loan to a teacher | due_date = today + `Teacher.MAX_LOAN_DAYS` (30), read from the subclass constant | ui: Avalos, Jeremiah (teacher), Animal Farm → loan 909 `(909, 166, 49, '2026-10-08', '2026-11-07', 'active')` | 2026-10-08 win | | pass |
| F4.4 | `return_loan(907, 53, today)` on a loan not yet due | returns 0, status 'returned', return_date today, copy back to 'available', one audit row | returned 0; loan `(907, 1, 'returned', '2026-10-04')`; copy `(1, 'available')`; audit `(2, 53, 'return_loan', 'Loans', 907)`. regression 2026-10-08: `returned: 0`, `[(907, 'returned', '2026-10-08')]`, `[(13, 'available')]` | 2026-10-04 win, 2026-10-08 win | | pass |
| F4.5 | `return_loan(887, 53, today)` — seeded overdue loan | days late computed correctly, loan returned, **no Fines row created** (fines are phase 6) | returned 30, matching 2026-09-04 → 2026-10-04 by hand. `COUNT(*) FROM Fines` was 2 before and 2 after | 2026-10-04 win | | pass |
| F4.6 | `mark_lost(904, 53)` on an active loan | Loans.status 'lost', return_date still NULL, copy 'lost', one audit row | loan `(904, 'lost', None)`; copy `(3, 'lost')`; audit `(4, 53, 'mark_lost', 904)` | 2026-10-04 win | | pass |
| F4.7 | BorrowingEligibility for the borrower before and after mark_lost | active_loans drops by one: a lost loan frees the slot | before `(52, 1)`, after `(52, 0)`. ui run: user 36 after loan 892 marked lost: view `(36, 1)`, Loans `[('active', 1), ('lost', 1), ('returned', 19)]` | 2026-10-04 win, 2026-10-08 win | | pass |
| F4.8 | `return_loan(904, 53, today)` — the lost book turns up | allowed, status 'returned', return_date today, copy 'available' | returned 5 days late; loan `(904, 'returned', '2026-10-04')` | 2026-10-04 win | | pass |

### functional — issue loan dialog and loans tab

| id | input | expected | actual | date | video | status |
|---|---|---|---|---|---|---|
| F4.3 | after loan 907 took copy 1, reopen the dialog on For Whom the Bell Tolls | only copy 2 offered | screenshot: copy box shows `-- Select Copy --` and `Copy 2 (new)` only | 2026-10-08 win | | pass |
| F4.9 | look at the Loans tab after issuing loan 907 | the new loan listed in due-date order with 14 days remaining | `Hester, Henley / For Whom the Bell Tolls / 1 / 2026-10-08 / 2026-10-22 / 14` | 2026-10-08 win | | pass |
| F4.10 | open the dialog | 700 × 560, `-- Select Borrower --`, Issue Loan disabled, red `*` on Borrower, Title, Copy, 200 titles as "Title by Author" | as expected | 2026-10-06 win | | pass (screen only) |
| F4.11 | open the borrower combo | "Last, First (homeroom)", sorted by last name; teachers "(teacher)"; inactive user 58 absent | as expected | 2026-10-06 win | | pass (screen only) |
| F4.12 | type `bell`, then `BELL` | For Whom the Bell Tolls listed both times (case-insensitive) | as expected | 2026-10-06 win | | pass (screen only) |
| F4.13 | type `shah` | Cal Shah's books listed (author match) | as expected | 2026-10-06 win | | pass (screen only) |
| F4.14 | type `zzz`, clear the box, then Cancel | empty list, no crash; all 200 back; dialog closes, AuditLog still 0 | AuditLog count `0` | 2026-10-06 win | | pass |
| F4.15 | open the dialog | eligibility blank, copy combo empty, Issue disabled | run, observation not written down | 2026-10-06 win | | re-run |
| F4.16 | pick borrower 42 (clean) | "Eligible to borrow" in normal colour, Issue still disabled | run, observation not written down | 2026-10-06 win | | re-run |
| F4.17 | 42, then For Whom the Bell Tolls | copy combo `-- Select Copy --`, `Copy 1 (new)`, `Copy 2 (new)`; Issue disabled | run, observation not written down | 2026-10-06 win | | re-run |
| F4.18 | pick Copy 1 | Issue Loan enabled | screenshot: Hester, Henley (13), "Eligible to borrow", Copy 1 (new), Issue Loan enabled | 2026-10-06 win | | pass |
| F4.19 | the teacher with an overdue loan (user 52) | "Eligible to borrow": overdue is not a block rule in phase 5 | | | | not run |
| F4.20 | issue through the ui: Hester (42), For Whom the Bell Tolls, Copy 1 | dialog closes; status "Loan 907 issued to Hester, Henley (13), due {today+14}." | screenshot: "Loan 907 issued to Hester, Henley (13), due 2026-10-22."; db row `(907, 1, 42, '2026-10-08', '2026-10-22', 'active')` | 2026-10-08 win | | pass |
| F4.21 | Return on the top overdue row (loan 887, due 2026-09-08), Yes | "Days late: 30."; row leaves Loans and Overdue | loan 887 `returned` 2026-10-08; audit `('return_loan', 887)`; overdue count fell | 2026-10-08 win | | pass (status screenshot owed) |
| F4.22 | Return on a loan not yet due (878, due 2026-10-19) | "Days late: 0." | `(878, 50, '2026-10-19', 'returned', '2026-10-08')`; copy 417 `available` | 2026-10-08 win | | pass (status screenshot owed) |
| F4.23 | Mark Lost on loan 892, Yes | "'…' marked as lost."; row gone from both tabs | `(892, 36, '2026-09-12', 'lost', None)`; copy 221 `lost`; audit `('mark_lost', 892)` | 2026-10-08 win | | pass (status screenshot owed) |

the 2026-10-08 return / lost run was done in a different order from the plan:
returns on 887, 886 and 878, then mark lost on 892. AuditLog read back
`[('return_loan', 887), ('return_loan', 886), ('return_loan', 878), ('mark_lost', 892)]`.

### structural — valid, extreme, invalid

| id | input | expected | actual | date | video | status |
|---|---|---|---|---|---|---|
| S4.1 | `check_eligibility(42)` — no loans, no fines | empty list | `[]` | 2026-10-04 win | | pass |
| S4.2 | `check_eligibility(43)` — exactly `Student.MAX_LOANS` active loans | blocked, message names the count and the limit | `['Borrower has reached the loan limit (3 of 3 loans)']`; after the full-stop fix `['Borrower has reached the loan limit (3 of 3 loans).']` | 2026-10-04 win, 2026-10-06 win | | pass |
| S4.3 | `check_eligibility(44)` — one unpaid fine | blocked, amount in PLN to 2 decimal places | `['Borrower has outstanding fines of 2.5 PLN.']`; after the `:.2f` fix `['Borrower has outstanding fines of 2.50 PLN.']` | 2026-10-04 win, 2026-10-06 win | | pass |
| S4.4 | `check_eligibility(45)` — only fine is **paid** | allowed: the block is on unpaid fines, not on ever being fined | `[]` | 2026-10-04 win | | pass |
| S4.5 | `check_eligibility(58)` — is_active = 0 | blocked; also absent from `get_borrowers()` | `['Account is inactive.']`; `get_borrowers()` returned 53 rows | 2026-10-04 win | | pass |
| S4.6 | borrower 43 after an unpaid fine was attached to one of their loans | **both** reasons returned | `['Borrower has reached the loan limit (3 of 3 loans)', 'Borrower has oustanding fines of 5.0 PLN.']` (fixture fine removed by reseeding; note the "oustanding" typo in that build, since fixed) | 2026-10-04 win | | pass |
| S4.7 | no borrower chosen, or no copy chosen | Issue Loan stays disabled, so nothing can be submitted (rewritten 2026-10-06: the dialog disables the button instead of showing a message) | see S4.17 and S4.18 | | | re-run |
| S4.8 | issue copy 1 again while still 'loaned' | ValueError "Copy is unavailable.", nothing written. the submit-time recheck cannot be triggered through the modal dialog on a single desk, so this repl run is the evidence | raised; `COUNT(*) FROM Loans` still 907 and AuditLog still 1. **message text not captured — re-run and paste it** | 2026-10-04 win | | pass (partial evidence) |
| S4.9 | insert a second active Loans row for a copy that already has one, in SQL | `UNIQUE constraint failed: Loans.copy_id` | | | | not run |
| S4.10 | issue_loan with user_id 99999 | refused, no Loans row, copy still 'available' | | | | not run |
| S4.11 | lend the last available copy of a title (copy 2 to Levy, loan 908), reopen | "No copies of this title are available." | screenshot shows the message in red with the copy box empty; book 1 `[(1,'loaned'),(2,'loaned'),(3,'loaned')]` | 2026-10-08 win | | pass |
| S4.12 | `return_loan(907, …)` on a loan already returned | ValueError, no second audit row | `ValueError: Loan has already been returned.`; AuditLog still 2. regression 2026-10-08 identical | 2026-10-04 win, 2026-10-08 win | | pass |
| S4.13 | a librarian as the borrower (53) | refused with a clear message | `ValueError: Only students and teachers can borrow`, raised in `users.get_user` | 2026-10-04 win | | pass |
| S4.14 | Copy 1 chosen, switch borrower to 43 | red loan-limit reason, Issue disabled | screenshot: Lim, Salem (7), red "…(3 of 3 loans).", Issue Loan disabled | 2026-10-06 win | | pass |
| S4.15 | switch to 44 | red fines reason, disabled | screenshot: Enriquez, Bella (8), red "…2.50 PLN.", disabled | 2026-10-06 win | | pass |
| S4.16 | switch to 45 (paid fine only) | "Eligible to borrow" **not red**, proving `setStyleSheet("")` resets the colour | screenshot: Levy, Jaycee (9), "Eligible to borrow" in black | 2026-10-08 win | | pass |
| S4.17 | back to `-- Select Borrower --` | label blank, disabled | run, observation not written down | 2026-10-06 win | | re-run |
| S4.18 | 42, then copy combo back to `-- Select Copy --` | disabled | run, observation not written down | 2026-10-06 win | | re-run |
| S4.19 | The Brothers Karamazov (book 2, no available copies) | "No copies of this title are available." in red, copy box empty, disabled | screenshot cropped above the message — retake | 2026-10-08 win | | re-run |
| S4.20 | title and copy chosen, then type `zzz` | list empty, copy combo emptied, disabled | run, observation not written down | 2026-10-06 win | | re-run |
| S4.21 | hidden Loan ID column holds the right loan_id for its row (column shown temporarily) | screen id matches the database | screen top row 887 / Nixon, Khloe; `[(887, 'Nixon')]` | 2026-10-08 win | | pass |
| S4.22 | Return with no row highlighted | "Select a loan first.", nothing written | message shown; AuditLog held exactly one row per real action afterwards | 2026-10-08 win | | pass (screen only) |
| S4.23 | highlight a row, Return, press Enter | nothing happens (No is the default) | row still listed; no extra audit row | 2026-10-08 win | | pass (screen only) |
| S4.24 | lost → discarded → returned: issue loan 908 on copy 16, mark_lost, discard_copy, return_loan | loan 'returned'; copy **stays 'discarded'** (the `AND status != 'discarded'` clause) | `returned: None` ×2, `returned: 0`; `[(908, 'returned', '2026-10-08')]`; `[(16, 'discarded')]` | 2026-10-08 win | | pass |
| S4.25 | X12: open Issue Loan, pick everything, Cancel | no status message, no Loans row, no audit row | only loans 907–909 and three audit rows existed afterwards | 2026-10-08 win | | pass |

S4.1 was run against a borrower holding **0** of 3 loans rather than
`MAX_LOANS - 1`. that still demonstrates "below the limit is allowed", but a row
at exactly 2 of 3 would be the tighter boundary and is worth adding.

---

## sc5 — overdue detection

| id | input | expected | actual | date | video | status |
|---|---|---|---|---|---|---|
| F5.1 | open the Overdue tab on the seeded database | exactly the seeded overdue loans, none of the active-but-not-due | 15 rows on screen against 60 active loans (before pass C fixtures existed; 16 since, see X7) | 2026-09-12 win | | pass |
| F5.2 | a known overdue loan | days overdue matches `today - due_date` by hand | top row due 2026-08-13 showed 30 days overdue on 2026-09-12 | 2026-09-12 win | | pass |
| F5.3 | sort order | worst first, days overdue descending | 30, 28, 26, 25 … 1 top to bottom | 2026-09-12 win | | pass |
| F5.4 | a loan marked lost whose due date has passed | not listed: the query filters `status = 'active'` | `892 in [row["loan_id"] for row in loans.get_overdue_loans(today)]` → `False`; overdue count 16 → 13 after 887, 886, 892 left | 2026-10-08 win | | pass |
| F5.5 | return every overdue loan, then reload | empty table renders with no error | | | | not run |
| S5.1 | the seeded loan due exactly today | **not** listed (strict `<`) | due 2026-09-12 shown in Loans at 0 days, absent from Overdue | 2026-09-12 win | | pass |
| S5.2 | the seeded loan due exactly yesterday | listed, one day overdue | due 2026-09-11 was the last Overdue row at 1 day | 2026-09-12 win | | pass |
| S5.3 | `get_overdue_loans` with an explicit past date | list changes, proving the date is a parameter, not sqlite's UTC `date('now')` | `get_overdue_loans("2026-08-20")` returned 4 where today returned 15 | 2026-09-12 win | | pass |

---

## sc6 — fines

phase 6. planned rows, written before any phase 6 code:

| id | input | expected | actual | date | video | status |
|---|---|---|---|---|---|---|
| F6.1 | late return spanning a weekend and a ClosedDays date | amount matches the rule worked out by hand; weekend and closed day not charged | | | | not run |
| F6.2 | return within the grace period | no Fines row | | | | not run |
| F6.3 | record payment on an unpaid fine | status paid, paid_date today, one audit row, `check_eligibility` now `[]` | | | | not run |
| F6.4 | mark_lost | one Fines row at the role maximum | | | | not run |
| S6.1 | return so late the uncapped amount exceeds max_amount | stored amount equals max_amount exactly | | | | not run |
| S6.2 | record payment on an already-paid fine | refused, no audit row | | | | not run |

---

## system-level tests

| id | input | expected | actual | date | video | status |
|---|---|---|---|---|---|---|
| X1 | Books schema change: add is_active, drop replacement_cost | is_active at index 6, replacement_cost gone, 16 tables, CHECK enforced | index 6; `COUNT = 200`; 16 tables; `CHECK constraint failed: is_active IN(0,1)` | 2026-07-31 win | | pass |
| X2 | run the app with no library.db present | should tell the user the database is missing | unhandled `sqlite3.OperationalError: no such table: Users` at login | 2026-09-?? mac | | **fail — not fixed** |
| X3 | seed fixtures for sc1 and sc4 exist after a reseed | 5 credentialed users; 2 inactive users; 46 StudentProfiles | `[(53,3,1,'librarian1'),(54,3,1,'librarian2'),(55,3,1,'librarian3'),(56,3,0,'inactive_librarian'),(57,2,1,'test_teacher')]`; `[(0,2),(1,56)]`; `46` | 2026-09-12 win | | pass |
| X4 | seed_loans pass A row count and status | 840 rows, every one 'returned', no copy left unavailable | `840`; `[('returned', 840)]`; `0` | 2026-09-12 win | | pass |
| X5 | no copy has two overlapping loan intervals | 0 overlaps, by construction | `0`; spot check on copy 1 | 2026-09-12 win | | pass |
| X6 | after pass B: active loans vs copies marked 'loaned' | equal | `(60, 60)` | 2026-09-28 mac | | pass |
| X7 | overdue split and boundary rows | after pass B: 15 with `due_date < today`. **after pass C: 16**, because the eligibility fixtures include a teacher with an overdue loan (loan 904, user 52) | pass B `15`, boundary rows 1 each (2026-09-12). pass C: overdue count `[(16,)]`; `[(904, 52, '2026-10-03')]` is the only fixture loan overdue | 2026-09-12 win, 2026-10-08 win | | pass |
| X8 | after pass C: the five eligibility fixtures | one borrower each for clean / at limit / unpaid fine / paid fine / inactive, plus a teacher with an overdue loan | read through `check_eligibility` (S4.1 to S4.5). **re-run as the raw BorrowingEligibility view for the video** | 2026-10-04 win | | pass (indirect) |
| X9 | `PRAGMA index_list('Loans')` | index_one_active_loan_per_copy present, `partial` = 1 | `[(0, 'index_one_active_loan_per_copy', 1, 'c', 1)]` | 2026-09-28 mac | | pass |
| X10 | reseed on a later date and re-run the counts | identical counts | 60 / 60 / 15 on 2026-09-12, 2026-09-28 and 2026-10-04 | 2026-10-04 win | | pass |
| X11 | X6 re-run after pass C and three ui loans | active loans = loaned copies | `[(67, 67)]` | 2026-10-08 win | | pass |
| X12 | see S4.25 | | | | | moved |

X10 is the evidence for the relative-dates decision. a fixed-date seeder would
have reported 34 overdue on 2026-10-04 for data built on 2026-09-12, which is
exactly what the stale database on the windows machine did before it was
reseeded.

known data gap: every seeded BookCopies row has `purchase_date = None`, so the
Purchase Date column is blank except for copies added through Add Copy. fix the
seeder or state it.

known behaviour: Save in edit mode writes an `edit_book` audit row even when no
field changed (seen 2026-10-04 as `(5, 53, 'edit_book', 'Books', 1, …)`).

---

## failures found and fixed

criterion d4 asks for failures and how they were fixed. these are worth more
than the passes.

| what broke | how it was found | fix |
|---|---|---|
| `QTableWidgetItem(1998)` — the one-argument overload takes an int *type code*, so the year column rendered blank | reading the table on screen | wrapped in `to_text()` |
| `get_all_books()` had no `SELECT` keyword | the app failed to load | added it |
| `if cur.fetchone is None` — method object compared to None, so the guard never fired | code review | added the parentheses |
| `Book.from_row` silently dropped four columns | `TypeError: 'Book' object is not subscriptable` on first Edit | deleted models/Book, `get_book()` returns the row |
| publication year `0` accepted and stored | reading a row back | floor raised to 1000 |
| `withdraw_book` wrote an audit row when zero rows were updated | code review | `cur.rowcount == 0` guard |
| `discard_copy` logged an already-discarded copy | code review | `AND status != 'discarded'` (replaced 2026-10-04 by an explicit status SELECT, see below) |
| copies table rendered above the book fields | opening the dialog | moved `addLayout(form)` above the copies block |
| three real librarians seeded with NULL username and hash | code review before running | restored the username scheme |
| fixture rows omitted `is_active`, so both "inactive" fixtures were active | code review | added `is_active` to the INSERT |
| `seed_loans` had its `executemany` inside the copy loop | code review before running | moved out to function level |
| `TABLE_NAMES` missing a comma, `"LoansFines"` | reading the list | added the comma |
| `seed_fixtures` blocks nested inside the at-limit loop | code review | dedented |
| `return_loan` whole `with con:` nested inside `if days_late < 0:` — on-time and late returns wrote nothing | code review | dedented |
| `con = get_connection` without parentheses, three times | each time at runtime | added the parentheses |
| `services/loans.py` overwritten twice by `users.py` content | `IndexError: No item with that key` | retyped; nothing had been committed |
| `user.is_active()` called on a model that exposes `get_is_active()` | runtime AttributeError | used the accessor |
| `withdraw_book` broken while adding the loaned-copy guard: `con = get_connection` (fourth time) **and** `"UPDAYE BookCopies"` — every withdrawal would have failed | code review before running, 2026-10-04 | fixed both; F3.4 re-run as F3.4r |
| `withdraw_book` and `discard_copy` skipped `con.close()` whenever their new guards raised | code review | `try/finally`, matching the other write functions |
| Discard Copy acted on a row the librarian never selected: `currentRow()` returns Qt's current cell, set to row 0 once the table has focus, so the `-1` guard did not fire | an unexplained discarded copy during testing, then reproduced on purpose (two screenshots: first click refused, second click discarded copy 1 with no row highlighted) | read `selectionModel().selectedRows()` in `_discard_copy` and `_edit_book` |
| `selected_rows[0].row` without parentheses passed a method object to `item()` | `TypeError … item(builtin_function_or_method, int)` on first Edit | `.row()` |
| `QMessageBox.standardButton` (lower-case s) in the new discard confirmation; would only have raised once a row was selected | code review | `StandardButton` |
| a confirmation answered Yes for the wrong copy during testing (row 3 click had not registered, box said copy 1) | an unexpected discarded copy; audit `discard_copy` on copy 1 at the same minute as the test | not a code bug. the message names the copy id so the librarian can check it against the book; criterion e point about confirmations being only as good as the reading of them |
| `tabs.addTab(loans_tab, "Loans")` lost while editing: the tab had no parent, so Qt deleted it, and the loan table with it, when `_setup_ui` returned | `RuntimeError: Internal C++ object (QTableWidget) already deleted` at launch | restored the line. widgets are kept alive by their parent, not by the python variable |
| `_filter_books` indented inside `_load_borrowers`, making it a local function (third indentation bug of this kind) | code review before running | dedented |
| issue loan dialog typos: class name `issueLoanDialog`, `_borrower_Box`, `_eligiblity_view`, `.click.connect` | code review before running | corrected |
| loan_id written to column 1 and immediately overwritten by the borrower, leaving hidden column 0 empty; Return would have crashed reading it | code review before Return existed | column index 0; confirmed by showing the column (S4.21) |
| Return and Mark Lost wiring copy-pasted from Issue Loan: `_mark_lost_button` never created, both handlers connected to the Issue Loan button | code review before running | each button connected to its own handler |
| `"avaliable"` typo in issue_loan made every copy look unavailable | code review | spelling fixed; F4.1 re-run |
| `(row["copy_id"])` with no comma is not a tuple: `ProgrammingError` on every return | regression run, traceback | `(row["copy_id"],)`. the crash happened between two UPDATEs and `with con:` rolled back the first (S2.2) |

the pattern across the early entries: code was declared finished without being
run or read back. the honest criterion e version is not "i made mistakes" but
"my testing checked for the absence of an exception rather than the correctness
of a result", and the fix was to query the database after every ui action
rather than trusting the screen.

the phase 5 entries add a second pattern: most were caught by reading the code,
and several would never have raised at the line where the mistake was. the
`return_loan` indentation bug, the column-1 overwrite and the `currentRow()`
discard all produced plausible screens while writing the wrong thing or nothing.
running `py_compile` on a file is not running it.

a third, process-level failure: working across two machines with nothing
committed cost most of one session recovering a file already written once. the
fix is a commit after every verified step.

a fourth, specific to copying blocks: the button wiring and the seeder loops both
failed because a pasted block kept names from the block it was copied from.
