from db.connection import get_connection
from models.student import Student
from models.teacher import Teacher


def get_borrowers():
    con = get_connection()
    cur = con.cursor()

    cur.execute("""SELECT Users.user_id, Users.first_name, Users.last_name, Roles.role_name, StudentProfiles.homeroom
                    FROM Users JOIN Roles ON Users.role_id = Roles.role_id
                    LEFT JOIN StudentProfiles ON Users.user_id = StudentProfiles.user_id WHERE Users.is_active = 1
                    AND Roles.role_name IN ('student', 'teacher')
                    ORDER BY Users.last_name, Users.first_name""")

    rows = cur.fetchall()
    con.close()
    return rows

def get_user(user_id):
    con = get_connection()
    cur = con.cursor()

    cur.execute("""SELECT Users.user_id, Users.first_name, Users.last_name,
                Users.email, Users.is_active, Roles.role_name,
                StudentProfiles.homeroom, Homerooms.year_number
                FROM Users
                JOIN Roles ON Users.role_id = Roles.role_id
                LEFT JOIN StudentProfiles ON Users.user_id = StudentProfiles.user_id
                LEFT JOIN Homerooms ON StudentProfiles.homeroom = Homerooms.homeroom
                WHERE Users.user_id = ?""", (user_id,))

    row = cur.fetchone()
    con.close()

    if row is None:
        raise ValueError("User not found")

    if row["role_name"] == "student":
        return Student.from_row(row)

    if row["role_name"] == "teacher":
        return Teacher.from_row(row)

    raise ValueError("Only students and teachers can borrow")