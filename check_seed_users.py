# checks the seeded users and the login rules against them
# run synthetic_data_generator.py first
import time
import bcrypt
from db.connection import get_connection
from services import auth
from models.librarian import Librarian

TEST_PASSWORD = "testpassword"

def check(test_id, description, passed):
    if passed:
        result = "pass"
    else:
        result = "FAIL"
    print(f"{test_id} {result}: {description}")\

def check_role_counts(con):
    cur = con.cursor()
    cur.execute("""SELECT role_name, COUNT(*) AS total FROM Users
                   JOIN Roles ON Users.role_id = Roles.role_id
                   GROUP BY role_name""")

    counts = {}
    for row in cur.fetchall():
        counts[row["role_name"]] = row["total"]

    check("X3.1", "46 students", counts.get("student") == 46)
    check("X3.2", "8 teachers", counts.get("teacher") == 8)
    check("X3.3", "4 librarians", counts.get("librarian") == 4)

def check_credentials(con):
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) AS total FROM Users WHERE username IS NOT NULL")
    check("X3.4", "exactly 5 users have credentials", cur.fetchone()["total"] == 5)

    cur.execute("""SELECT COUNT(*) AS total FROM Users
                   JOIN Roles ON Users.role_id = Roles.role_id
                   WHERE role_name = 'student' AND username IS NOT NULL""")
    check("X3.5", "no student has credentials", cur.fetchone()["total"] == 0)

    cur.execute("SELECT COUNT(*) AS total FROM Users WHERE is_active = 0")
    check("X3.6", "exactly 2 inactive users", cur.fetchone()["total"] == 2)

    cur.execute("""SELECT DISTINCT typeof(password_hash) AS kind FROM Users
                   WHERE password_hash IS NOT NULL""")
    kinds = cur.fetchall()
    check("X3.7", "every hash is stored as text", len(kinds) == 1 and kinds[0]["kind"] == "text")

def get_user_by_username(con, username):
    cur = con.cursor()
    cur.execute("""SELECT Users.is_active, Users.password_hash, Roles.role_name FROM Users
                   JOIN Roles ON Users.role_id = Roles.role_id
                   WHERE username = ?""", (username,))
    return cur.fetchone()

def password_matches(row):
    return bcrypt.checkpw(TEST_PASSWORD.encode(), row["password_hash"].encode())

def check_fixtures(con):
    inactive = get_user_by_username(con, "inactive_librarian")
    # the None check has to come first or the next part crashes
    check("X3.8", "inactive_librarian is a librarian, inactive, with the correct password",
          inactive is not None
          and inactive["role_name"] == "librarian"
          and inactive["is_active"] == 0
          and password_matches(inactive))

    teacher = get_user_by_username(con, "test_teacher")
    check("X3.9", "test_teacher is an active teacher with the correct password",
          teacher is not None
          and teacher["role_name"] == "teacher"
          and teacher["is_active"] == 1
          and password_matches(teacher))

def check_logins():
    start = time.perf_counter()
    librarian = auth.login("librarian1", TEST_PASSWORD)
    elapsed = time.perf_counter() - start

    check("F1.1", "active librarian logs in and gets a Librarian back", isinstance(librarian, Librarian))
    check("F1.7", f"login took {elapsed:.2f}s, under 2 seconds", elapsed < 2)
    check("F1.5", "inactive librarian with the correct password is refused",
          auth.login("inactive_librarian", TEST_PASSWORD) is None)
    check("F1.6", "teacher with a valid hash is refused",
          auth.login("test_teacher", TEST_PASSWORD) is None)
    check("F1.3", "unknown username is refused", auth.login("nobody", TEST_PASSWORD) is None)
    check("S1.1", "injection string is treated as a plain username",
          auth.login("' OR '1'='1", TEST_PASSWORD) is None)

def main():
    con = get_connection()
    check_role_counts(con)
    check_credentials(con)
    check_fixtures(con)
    con.close()

    check_logins()

if __name__ == "__main__":
    main()

