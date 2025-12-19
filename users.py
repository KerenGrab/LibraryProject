from db import get_connection


def create_user(name, phone=None, email=None):
    """
    Creates a new user in the Users table.

    :param name: str - user full name (required)
    :param phone: str or None - user's phone number (optional)
    :param email: str or None - user's email (optional, UNIQUE if not NULL)
    :return: int - the newly created user_id
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO Users (name, phone, email)
        VALUES (?, ?, ?)
    """, (name, phone, email))

    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id


def get_user(user_id):
    """
    Fetches a single user by user_id.
    :return: sqlite3.Row or None
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, name, phone, email
        FROM Users
        WHERE user_id = ?
    """, (user_id,))

    row = cur.fetchone()
    conn.close()
    return row


def find_user_by_phone(phone):
    """
    Fetches a user by exact phone match.
    :return: sqlite3.Row or None
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, name, phone, email
        FROM Users
        WHERE phone = ?
    """, (phone,))

    row = cur.fetchone()
    conn.close()
    return row


def find_user_by_email(email):
    """
    Fetches a user by exact email match.
    :return: sqlite3.Row or None
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, name, phone, email
        FROM Users
        WHERE email = ?
    """, (email,))

    row = cur.fetchone()
    conn.close()
    return row


def list_users():
    """
    Returns all users from the Users table.
    :return: list[sqlite3.Row]
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, name, phone, email
        FROM Users
        ORDER BY name
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


def update_user(user_id, name=None, phone=None, email=None):
    """
    Updates one or more fields of an existing user.
    Only fields that are not None will be updated.
    :return: bool
    """
    if name is None and phone is None and email is None:
        return False

    conn = get_connection()
    cur = conn.cursor()

    fields = []
    params = []

    if name is not None:
        fields.append("name = ?")
        params.append(name)

    if phone is not None:
        fields.append("phone = ?")
        params.append(phone)

    if email is not None:
        fields.append("email = ?")
        params.append(email)

    params.append(user_id)

    cur.execute(f"""
        UPDATE Users
        SET {", ".join(fields)}
        WHERE user_id = ?
    """, tuple(params))

    conn.commit()
    updated = (cur.rowcount > 0)
    conn.close()
    return updated


def delete_user(user_id):
    """
    Deletes a user by user_id.

    Policy:
    - Do not delete a user if they have active borrows (return_date IS NULL).
      In that case, return False.

    :return: bool
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*) AS cnt
        FROM Borrow
        WHERE user_id = ?
          AND return_date IS NULL
    """, (user_id,))
    active_count = cur.fetchone()["cnt"]

    if active_count > 0:
        conn.close()
        return False

    cur.execute("""
        DELETE FROM Users
        WHERE user_id = ?
    """ , (user_id,))

    conn.commit()
    deleted = (cur.rowcount > 0)
    conn.close()
    return deleted


def borrowed_books_of_user(user_id, active_only=True):
    """
    Returns the books borrowed by a user (JOIN Borrow + Books).
    :return: list[sqlite3.Row]
    """
    conn = get_connection()
    cur = conn.cursor()

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

    rows = cur.fetchall()
    conn.close()
    return rows


def count_borrowed_books_of_user(user_id, active_only=True):
    """
    Counts how many books a user has borrowed.
    :return: int
    """
    conn = get_connection()
    cur = conn.cursor()

    if active_only:
        cur.execute("""
            SELECT COUNT(*) AS cnt
            FROM Borrow
            WHERE user_id = ?
              AND return_date IS NULL
        """, (user_id,))
    else:
        cur.execute("""
            SELECT COUNT(*) AS cnt
            FROM Borrow
            WHERE user_id = ?
        """, (user_id,))

    count = cur.fetchone()["cnt"]
    conn.close()
    return count
