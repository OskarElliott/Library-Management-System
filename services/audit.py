from db.connection import get_connection

def get_audit_log():
    con = get_connection()

    try:
        cur = con.cursor()
        cur.execute("""SELECT datetime(AuditLog.logged_at, 'localtime') AS local_time,
                    Users.first_name, Users.last_name, AuditLog.action, AuditLog.table_name, AuditLog.record_id
                    FROM AuditLog JOIN Users ON AuditLog.user_id = Users.user_id
                    ORDER BY AuditLog.log_id DESC""")
        
        rows = cur.fetchall()

    finally:
        con.close()

    return rows