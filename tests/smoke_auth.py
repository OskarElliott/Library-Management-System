from getpass import getpass
from db.connection import get_connection
from services.auth_service import AuthService

def main():
    conn = get_connection()
    auth = AuthService(conn)

    username = input("username: ").strip()
    password = getpass("password: ")

    user = auth.login(username, password)
    if user is None:
        print("login failed")
        return
    
    print(f"logged in as {user.username} ({user.role_name})")
    print(f"max loan days: {user.max_loan_days()}")
    print(f"max loans: {user.max_loans()}")

    row = conn.execute(
        "SELECT outstanding_fines, active_loans "
        "FROM borrowing_eligibility WHERE user_id = ?",
        (user.user_id,),
    ).fetchone()

    fines = row["outstanding_fines"]
    loans = row["active_loans"]
    print(f"outstanding fines: {fines} PLN, active loans: {loans}")
    print("can borrow:", user.can_borrow(fines, loans))

if __name__ == "__main__":
    main()