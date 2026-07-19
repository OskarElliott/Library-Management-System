# project context

last updated: 2026-07-19 (fresh restart, environment setup)

this is my private reference doc for the project. it is not part of the ia
submission. i paste it into new ai chats so i don't have to re-explain everything
from scratch. if something here clashes with a decision i've since changed, the
date at the top is the tie-breaker and i should fix the doc.

read this first, then CONVENTIONS.md for the coding rules.

## what and why

a library management system for my school library, built as my ib computer
science sl internal assessment (2027 session). the ia is worth 30% of the sl
grade.

right now the library runs on paper. there's no real record of who has what, so
students keep books for months, and the librarian has no data to decide what to
buy next. the system fixes the boring but real problems: track loans, spot
overdue books, charge fines, and later give the librarian some numbers to guide
purchasing.

## who it's for

- me: builder, ib student.
- client / main user: the head librarian. runs the system at the front desk.
- other users: teachers (longer loans) and students (borrow lookup, and
  reservations if i get that far).

consent: the pre-planning sheet requires written client consent, stored
securely. i'm keeping the librarian-as-client framing. the real interview and
signed consent happen before final submission. for now i'm working from how i've
seen the library actually run plus supervisor guidance.

## the ia rules that shape everything

from IB_CS_IA_Pre_Planning_Sheet.pdf (that sheet wins over any general "how ib
ias work" advice):

- 30 marks total, 2000 word limit for the documentation.
- criteria: a problem spec (4 marks, ~300 words), b planning (4, ~150),
  c system overview (6, ~150), d development (12, ~1000), e evaluation (4, ~400).
- one pdf, five labelled sections a to e. full source code in a separate
  appendix. video max 5 minutes showing it working plus testing.
- success criteria from a must be referenced again in b, d and e.

## scope: core first, extensions if there's time

the plan is a committed core that is a complete, working library system on its
own, plus extensions i only add if the hours allow. the point is to finish
something that fully does what it says, not half-build lots of features. the
success criteria i agree with the client match the core; the extensions are
"further criteria if scope permits."

committed core (this is the whole promise):
1. login with three roles (student, teacher, librarian) and role-based access
2. book and copy management (librarian can add / edit / remove)
3. borrow and return
4. overdue detection, worked out from the due date
5. fines (grace period, rising daily rate, capped per role; unpaid fines block
   borrowing)

extensions, added in this order only if time allows:
1. google books api (fill in book details from an isbn)
2. demand analytics (simple loan-count ranking, nothing clever)
3. email notifications over smtp (overdue warnings)
4. reservations (queue for books that are all out on loan) — most complex, last
   or cut

descoped, written up as future work in criterion e:
- recommender (per-student book suggestions). was going to be cosine similarity
  on genre vectors. cut to keep the core finishable. good honest e2 material:
  explain what it would do and why it was out of scope for the time budget.

## success criteria

core (these are the real promise, all measurable / testable):

- sc1 roles and login: student, teacher and librarian each log in with a
  bcrypt-hashed password within about 2 seconds; each role can only reach the
  actions allowed for that role.
- sc2 data safety: passwords are only ever stored as bcrypt hashes; every sql
  query is parameterised; an audit log records admin actions (adding or removing
  books, issuing loans, changing fines) with a timestamp and the user id.
- sc3 books and copies: the librarian can add, edit and remove book titles and
  their physical copies; one title can have many copies.
- sc4 borrow and return: the librarian can lend an available copy to a user with
  a due date and record its return; a user who is over their loan limit or has
  unpaid fines is blocked from borrowing (checked through the eligibility view).
- sc5 overdue: the system decides which loans are overdue from the due date vs
  today's date (never stored) and can list them.
- sc6 fines: after a grace period a fine builds up at a rising daily rate, capped
  at the per-role maximum in FineRules.max_amount; a late return produces a fine
  automatically and unpaid fines block new loans.

extensions (only if scope permits):

- sc7 isbn lookup: given a valid 13-digit isbn, book details come back from the
  google books api and get filled in within about 3 seconds, with a manual
  fallback if the lookup fails.
- sc8 demand analytics: books and genres are ranked by how many times they've
  been borrowed, to help the librarian decide what to buy. plain count, no
  weighting or forecasting.
- sc9 email: overdue warnings can be sent by email over smtp.
- sc10 reservations: a user can reserve a title that is currently all on loan and
  is queued (staff before students, then first come first served).

## tech stack

core needs only these:
- python 3.13 (stdlib does a lot of the work)
- pyside6 for the desktop ui
- sqlite through the standard library sqlite3, no orm
- bcrypt for password hashing

extension-only dependencies, added when i reach the phase that needs them (not
before, so requirements.txt stays honest to what's actually used):
- requests for the google books api call
- matplotlib for the analytics chart
- smtplib (stdlib) for email

why these, short version:
- sqlite: no separate server, one file, transactional, right size for a
  single-librarian desktop app. limit: it serialises writes, so a real
  school-wide multi-user version would want postgres. good criterion d/e point.
- direct sqlite3 over an orm: keeps the sql visible so the moderator can see i
  understand it, and keeps the moving parts low.
- pyside6 over tkinter: better looking, has signals/slots and table models that
  fit the app.
- bcrypt: salted, slow on purpose, standard for passwords.

## architecture

three layers, ui at the top, database at the bottom, services in between:

    ui (pyside6)          login window, main window, the views
        |  calls
    services              auth, books, loans, fines, and later analytics /
        |  calls          reservations / notifications
    db (sqlite3)          connection.py, schema.sql, the eligibility view

rules:
- the ui never touches the database directly. it goes through a service.
- domain classes (the user hierarchy, book, loan) live in models/.
- one shared notification service later handles both overdue and reservation
  emails, so there's one smtp setup.

## user class hierarchy (locked design)

drawn as a uml class diagram before writing any code (course-text convention and
criterion b evidence).

- User is abstract. i never make a plain User. every person is a Student,
  Teacher or Librarian.
- what differs between them is borrowing behaviour. the loan limits MAX_LOANS and
  MAX_LOAN_DAYS are class-level constants set per subclass, not methods that get
  overridden, because they are fixed values for a role, not a calculation. base
  User sets both to 0 as a fail-safe so a missing subclass can't accidentally
  borrow.
- Student also carries profile data staff don't have (year number, homeroom,
  form tutor email), pulled from a Users + StudentProfiles join.
- Teacher and Librarian are separate classes even though their data looks
  identical right now, because Librarian gains admin methods later (add / remove
  books, issue loans, adjust fines) that a Teacher never has.

## database schema

16 tables plus one view. schema.sql becomes the source of truth once i build it
in phase 1; until then this section is the design i build from.

groups:
- identity: Roles, Users, StudentProfiles
- catalogue: Publishers, Genres, Authors, Books, BookAuthors, BookCopies
- circulation: Loans, Reservations
- fines: FineRules, Fines
- operations: SchoolCalendar, Notifications, AuditLog

key columns (rough, schema.sql pins the exact names):

    Roles(role_id PK, role_name UK, description)
    Users(user_id PK, username UK, password_hash, role_id FK, email,
          created_at, is_active)
    StudentProfiles(user_id PK/FK, year_number, homeroom, form_tutor_email)
      -- year_number CHECK between 7 and 13 (ib1/ib2 stored as 12/13)

    Publishers(publisher_id PK, name UK, country)
    Genres(genre_id PK, name UK)
      -- flat, no parent genre
    Authors(author_id PK, first_name, last_name)
    Books(book_id PK, isbn UK, title, publication_year, publisher_id FK,
          genre_id FK, description, replacement_cost)
    BookAuthors(book_id FK, author_id FK, composite PK)
    BookCopies(copy_id PK, book_id FK, purchase_date, condition, status)

    Loans(loan_id PK, copy_id FK, user_id FK, checkout_date, due_date,
          return_date NULL, status)
      -- status: active | returned | lost. overdue is computed, never stored
    Reservations(reservation_id PK, book_id FK, user_id FK, request_date,
                 priority, status, notified_date NULL, expires_at NULL)
      -- reservations point at a title (book_id), not a copy

    FineRules(rule_id PK, role_id FK UNIQUE, grace_days, tier_1_rate,
              tier_2_rate, max_amount)
    Fines(fine_id PK, loan_id FK, amount, issued_date, paid_date NULL, status)

    SchoolCalendar(day_date PK, is_open, day_type, notes)
    Notifications(notification_id PK, loan_id FK NULL, recipient_id FK, type,
                  recipient_email, sent_at, status)
    AuditLog(log_id PK, user_id FK, action, table_name, record_id, logged_at)

the eligibility view is the single answer to "can this user borrow?" it sums
unpaid fines and counts active loans per user:

    CREATE VIEW borrowing_eligibility AS
    SELECT u.user_id,
           COALESCE(SUM(CASE WHEN f.status='unpaid' THEN f.amount END), 0)
             AS outstanding_fines,
           COUNT(DISTINCT CASE WHEN l.return_date IS NULL THEN l.loan_id END)
             AS active_loans
    FROM Users u
    LEFT JOIN Loans l ON l.user_id = u.user_id
    LEFT JOIN Fines f ON f.loan_id = l.loan_id
    GROUP BY u.user_id;

COUNT(DISTINCT ...) is there on purpose. joining loans and fines multiplies rows
(one loan with two fines shows up twice), so a plain count would over-count
active loans. COALESCE turns a null sum into 0 for users with no fines.

## some design decisions i can defend (criterion d)

short versions, i'll expand these when writing the ia:

- separate Books from BookCopies: a title is an idea, a copy is a physical
  object on a shelf. loans attach to a copy, reservations attach to a title,
  because a student reserving a book doesn't care which copy they get.
- FineRules separate from Fines: rules are the current policy, fines are things
  that already happened. changing the rate shouldn't rewrite old fines.
- fine cap is the flat per-role FineRules.max_amount, not the book's replacement
  cost. simpler and it's a policy the librarian sets.
- overdue computed, not stored: a stored flag would go stale the moment a day
  passes. computing from the due date is always correct.
- sql view for eligibility instead of a python loop: one place that answers the
  question, set-based, easy to read and test.
- dropped a StaffProfiles table: its only real column was subject, which nothing
  in the system actually uses. staff permissions are the same for everyone in a
  role, so they live in Roles plus the Teacher / Librarian classes plus service
  checks. kept StudentProfiles because form_tutor_email genuinely varies per
  student and drives the tutor email copy. a table only earns its place when it
  holds a per-person attribute the system acts on.
- is_active flag instead of deleting users: keeps history. AuthService.login
  must check it so a deactivated user can't log in. (reminder to self: enforce
  this in phase 2.)

## build plan

roughly 35 hours. build in order. each phase should end with something i can
actually run. core has to be done before any extension starts.

phase 0  environment setup (venv, deps, git, github)   -- doing now
phase 1  schema.sql + db/connection.py + synthetic data seeder
phase 2  auth: bcrypt + user hierarchy + a cli smoke test
phase 3  minimal pyside6 shell (login window + a books table)
phase 4  book and copy crud (manual add / edit / remove)
phase 5  borrow / return + overdue detection
phase 6  fines + fine rules + school calendar + eligibility view
         -- core complete here --
phase 7  google books api (isbn lookup layered onto crud)   [extension]
phase 8  demand analytics (loan-count ranking + a chart)    [extension]
phase 9  email over smtp (overdue warnings)                 [extension]
phase 10 reservations                                       [extension]
phase 11 testing + ui polish
phase 12 documentation + video

if i run over time, cut from the bottom: reservations first, then email, then
analytics. never cut into the core.

## things not to do (already decided)

- no orm. direct sqlite3.
- parameterised queries everywhere. never build sql by joining strings.
- nothing sensitive in plaintext. bcrypt for passwords.
- don't build out of phase order. schema before auth, auth before ui, ui shell
  before features, core before extensions.
- don't build the recommender. it's descoped, it's future work only.
- keep analytics simple: a loan count. no recency weighting, no regression, no
  seasonality.
- genres stay flat. no parent genre.
- loan limits are class constants, not overridden methods.
- don't switch ui framework. pyside6 is locked.
- don't write the ia as i go. keep a dev journal, compress it into the ia at the
  end.
- currency is pln everywhere.

## synthetic data

there's no real loan history, so i generate fake data to test everything,
especially the analytics later. generate_synthetic_data.py sits at the repo root.
it wipes and rebuilds library.db from schema.sql each run, uses random.seed(42)
so it's reproducible, and hashes one shared dev password once with bcrypt and
reuses it for all seed users.

rough targets: ~55 users (students across years 7-11 + ib1 + ib2, a few teachers,
one librarian), ~200 books, ~648 copies, ~800 past loans, plus some active and
overdue loans. popularity follows a rough 80/20 split (a small popular set gets
most of the loans) using random.choices, so ranking has something to find.

kept simple on purpose: no month-by-month trend engine, no per-student taste
clusters, no custom weighting. those were for the cut recommender and the old
weighted analytics, so they're gone.