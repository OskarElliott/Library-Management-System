[1mdiff --git a/services/books.py b/services/books.py[m
[1mindex 848ea47..6ecb5e3 100644[m
[1m--- a/services/books.py[m
[1m+++ b/services/books.py[m
[36m@@ -173,24 +173,17 @@[m [mdef edit_book(book_id, isbn, title, genre_id, publication_year, publisher, autho[m
     finally:[m
         con.close()[m
 [m
[31m-def withdraw_book(book_id, librarian_id):[m
[32m+[m[32mdef get_available_copies(book_id):[m
     con = get_connection()[m
[32m+[m[32m    cur = con.cursor()[m
 [m
[31m-    try:[m
[31m-        with con:[m
[31m-            cur = con.cursor()[m
[31m-[m
[31m-            cur.execute("UPDATE Books SET is_active = 0 WHERE book_id = ?", (book_id,))[m
[31m-[m
[31m-            if cur.rowcount == 0:[m
[31m-                raise ValueError("Book not found")[m
[31m-[m
[31m-            cur.execute("UPDATE BookCopies SET status = 'discarded' WHERE book_id = ?", (book_id,))[m
[32m+[m[32m    cur.execute("""SELECT copy_id, condition FROM BookCopies WHERE book_id = ? AND status = 'available'[m
[32m+[m[32m                    ORDER BY copy_id""", (book_id,))[m
 [m
[31m-            cur.execute("INSERT INTO AuditLog(user_id, action, table_name, record_id) VALUES (?,?,?,?)", (librarian_id, ACTION_WITHDRAW_BOOK, "Books", book_id))[m
[32m+[m[32m    copies = cur.fetchall()[m
[32m+[m[32m    con.close()[m
 [m
[31m-    finally:[m
[31m-        con.close()[m
[32m+[m[32m    return copies[m
 [m
 def add_copy(book_id, librarian_id):[m
     purchase_date = date.today().isoformat() # default purchase date[m
[36m@@ -215,20 +208,56 @@[m [mdef add_copy(book_id, librarian_id):[m
     finally:[m
         con.close()[m
 [m
[31m-def discard_copy(copy_id, librarian_id):[m
[32m+[m[32mdef withdraw_book(book_id, librarian_id):[m
     con = get_connection()[m
 [m
     try:[m
         with con:[m
             cur = con.cursor()[m
 [m
[31m-            cur.execute("UPDATE BookCopies SET status = 'discarded' WHERE copy_id = ? AND status != 'discarded'", (copy_id,))[m
[32m+[m[32m            cur.execute("SELECT COUNT(*) FROM BookCopies WHERE book_id = ? AND status = 'loaned'", (book_id,))[m
[32m+[m
[32m+[m[32m            loaned_count = cur.fetchone()[0][m
[32m+[m
[32m+[m[32m            if loaned_count > 0:[m
[32m+[m[32m                raise ValueError(f"{loaned_count} copies of this title are on loan.")[m
[32m+[m
[32m+[m[32m            cur.execute("UPDATE Books SET is_active = 0 WHERE book_id = ?", (book_id,))[m
 [m
             if cur.rowcount == 0:[m
[31m-                raise ValueError("Copy not found or already discarded")[m
[32m+[m[32m                raise ValueError("Book not found.")[m
 [m
[31m-            cur.execute("INSERT INTO AuditLog(user_id, action, table_name, record_id) VALUES(?, ?, ?, ?)", (librarian_id, ACTION_DISCARD_COPY, "BookCopies", copy_id))[m
[32m+[m[32m            cur.execute("UPDATE BookCopies SET status = 'discarded' WHERE book_id = ?", (book_id,))[m
 [m
[31m-    finally: [m
[32m+[m[32m            cur.execute("INSERT INTO AuditLog(user_id, action, table_name, record_id) VALUES (?,?,?,?)", (librarian_id, ACTION_WITHDRAW_BOOK, "Books", book_id))[m
[32m+[m
[32m+[m[32m    finally:[m
         con.close()[m
 [m
[32m+[m[32mdef discard_copy(copy_id, librarian_id):[m
[32m+[m[32m    con = get_connection()[m
[32m+[m
[32m+[m[32m    try:[m
[32m+[m[32m        with con:[m
[32m+[m[32m            cur = con.cursor()[m
[32m+[m
[32m+[m[32m            cur.execute("SELECT status FROM BookCopies WHERE copy_id = ?", (copy_id,))[m
[32m+[m
[32m+[m[32m            row = cur.fetchone()[m
[32m+[m
[32m+[m[32m            if row is None:[m
[32m+[m[32m                raise ValueError("Copy not found")[m
[32m+[m
[32m+[m[32m            if row["status"] == "loaned":[m
[32m+[m[32m                raise ValueError("Copy is on loan, it must be returned before discarding.")[m
[32m+[m
[32m+[m[32m            if row["status"] == "discarded":[m
[32m+[m[32m                raise ValueError("Copy is already discarded.")[m
[32m+[m
[32m+[m[32m            cur.execute("UPDATE BookCopies SET status = 'discarded' WHERE copy_id = ?", (copy_id,))[m
[32m+[m
[32m+[m[32m            cur.execute("INSERT INTO AuditLog(user_id, action, table_name, record_id) VALUES (?,?,?,?)", (librarian_id, ACTION_DISCARD_COPY, "BookCopies", copy_id))[m
[32m+[m
[32m+[m[32m    finally:[m
[32m+[m[32m        con.close()[m
[32m+[m[41m        [m
\ No newline at end of file[m
[1mdiff --git a/ui/book_dialog.py b/ui/book_dialog.py[m
[1mindex 72319f6..5bfa1fc 100644[m
[1m--- a/ui/book_dialog.py[m
[1m+++ b/ui/book_dialog.py[m
[36m@@ -135,7 +135,7 @@[m [mclass BookDialog(QDialog):[m
 [m
     def _withdraw(self):[m
         answer = QMessageBox.question(self, "Withdraw Book", "Are you sure you want to withdraw this book?\nAll copies will be discarded.",[m
[31m-                                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)[m
[32m+[m[32m                                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No,)[m
 [m
         if answer != QMessageBox.StandardButton.Yes:[m
             return[m
