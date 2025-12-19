from db import get_connection

"""
Borrow logic: handles borrowing/returning actions + queries (mostly JOINs with Books/Users).

Schema note:
- This file assumes Users has: user_id, name, phone, email
"""


def borrow_book(user_id, book_id, borrow_date):
    """
    Borrows a book for a user.

    Creates a new row in Borrow (return_date stays NULL) and marks the book copy as unavailable
    in Books (available = 0).

    Policy:
    - Borrow only if the user exists.
    - Borrow only if the book exists AND is available.
    - Uses atomic update on Books to prevent double-borrow.

    :return: int or None - new borrow_id if successful, else None
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        # verify user exists
        cur.execute("""
            SELECT 1
            FROM Users
            WHERE user_id = ?
        """, (user_id,))
        if cur.fetchone() is None:
            return None

        # mark book unavailable only if it is currently available
        cur.execute("""
            UPDATE Books
            SET available = 0
            WHERE book_id = ?
              AND available = 1
        """, (book_id,))
        if cur.rowcount == 0:
            return None

        # insert borrow row
        cur.execute("""
            INSERT INTO Borrow (book_id, user_id, borrow_date, return_date)
            VALUES (?, ?, ?, NULL)
        """, (book_id, user_id, borrow_date))

        borrow_id = cur.lastrowid
        conn.commit()
        return borrow_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def return_book(borrow_id, return_date):
    """
    Returns a borrowed book.

    Policy:
    - Only succeeds if borrow_id exists AND is currently active (return_date IS NULL).

    :return: bool
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        # find the active borrow and its book_id
        cur.execute("""
            SELECT book_id
            FROM Borrow
            WHERE borrow_id = ?
              AND return_date IS NULL
        """, (borrow_id,))
        row = cur.fetchone()
        if row is None:
            return False

        book_id = row["book_id"]

        # close the borrow
        cur.execute("""
            UPDATE Borrow
            SET return_date = ?
            WHERE borrow_id = ?
              AND return_date IS NULL
        """, (return_date, borrow_id))
        if cur.rowcount == 0:
            return False

        # mark book available again
        cur.execute("""
            UPDATE Books
            SET available = 1
            WHERE book_id = ?
        """, (book_id,))

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def list_user_borrows(user_id, active_only=True):
    """
    Returns borrows of a given user (JOIN Borrow + Books).
    :return: list[sqlite3.Row]
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        if active_only:
            cur.execute("""
                SELECT
                    b.borrow_id,
                    b.book_id,
                    bk.title,
                    bk.author,
                    bk.year,
                    b.borrow_date,
                    b.return_date
                FROM Borrow AS b
                JOIN Books  AS bk ON bk.book_id = b.book_id
                WHERE b.user_id = ?
                  AND b.return_date IS NULL
                ORDER BY b.borrow_date DESC
            """, (user_id,))
        else:
            cur.execute("""
                SELECT
                    b.borrow_id,
                    b.book_id,
                    bk.title,
                    bk.author,
                    bk.year,
                    b.borrow_date,
                    b.return_date
                FROM Borrow AS b
                JOIN Books  AS bk ON bk.book_id = b.book_id
                WHERE b.user_id = ?
                ORDER BY b.borrow_date DESC
            """, (user_id,))

        return cur.fetchall()

    finally:
        conn.close()


def list_active_borrows():
    """
    Returns all currently active borrows (return_date IS NULL), with user + book details.
    :return: list[sqlite3.Row]
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                b.borrow_id,
                b.borrow_date,
                b.book_id,
                bk.title,
                bk.author,
                bk.year,
                u.user_id,
                u.name,
                u.phone,
                u.email
            FROM Borrow AS b
            JOIN Books  AS bk ON bk.book_id = b.book_id
            JOIN Users  AS u  ON u.user_id  = b.user_id
            WHERE b.return_date IS NULL
            ORDER BY b.borrow_date DESC
        """)
        return cur.fetchall()

    finally:
        conn.close()


def list_active_users():
    """
    Returns distinct users that currently have at least one active borrow.
    :return: list[sqlite3.Row]
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT DISTINCT
                u.user_id,
                u.name,
                u.phone,
                u.email
            FROM Borrow AS b
            JOIN Users  AS u ON u.user_id = b.user_id
            WHERE b.return_date IS NULL
            ORDER BY u.name
        """)
        return cur.fetchall()

    finally:
        conn.close()


def list_borrow_history():
    """
    Returns full borrow history (active + returned), with user + book details.
    :return: list[sqlite3.Row]
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                b.borrow_id,
                b.borrow_date,
                b.return_date,
                b.book_id,
                bk.title,
                bk.author,
                bk.year,
                u.user_id,
                u.name,
                u.phone,
                u.email
            FROM Borrow AS b
            JOIN Books  AS bk ON bk.book_id = b.book_id
            JOIN Users  AS u  ON u.user_id  = b.user_id
            ORDER BY b.borrow_date DESC, b.return_date DESC
        """)
        return cur.fetchall()

    finally:
        conn.close()


def list_users_who_borrowed_book(book_id):
    """
    Returns users (and borrow/return dates) who borrowed a specific book copy.
    :return: list[sqlite3.Row]
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                u.user_id,
                u.name,
                u.phone,
                u.email,
                b.borrow_id,
                b.borrow_date,
                b.return_date
            FROM Borrow AS b
            JOIN Users  AS u ON u.user_id = b.user_id
            WHERE b.book_id = ?
            ORDER BY b.borrow_date DESC
        """, (book_id,))
        return cur.fetchall()

    finally:
        conn.close()


def get_user_id_by_phone(phone):
    """
    Returns the user_id associated with a phone number, or None if not found.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT user_id
            FROM Users
            WHERE phone = ?
        """, (phone,))
        row = cur.fetchone()
        return None if row is None else row["user_id"]

    finally:
        conn.close()


def list_borrows_by_phone(phone, active_only=True):
    """
    Convenience wrapper:
    - find user_id by phone
    - return list_user_borrows(user_id, active_only)
    """
    user_id = get_user_id_by_phone(phone)
    if user_id is None:
        return []
    return list_user_borrows(user_id, active_only=active_only)
