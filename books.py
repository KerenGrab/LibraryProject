from db import get_connection


def add_book(title, author, year=None):
    """
    Adds a new book to the Books table. It will add a new row.

    Note: Duplicates are allowed intentionally, because the library may own multiple copies
    of the same book (same title/author/year), and each copy is stored as a separate row
    with its own book_id.

    :param title: str - book title
    :param author: str - book author
    :param year: int or None - publication year (optional)
    :return: int - the new book_id
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO Books (title, author, year, available)
        VALUES (?, ?, ?, 1)
    """, (title, author, year))

    conn.commit()
    book_id = cur.lastrowid
    conn.close()
    return book_id


def list_books():
    """
    Returns all books from the Books table.
    :return: list[sqlite3.Row] - rows containing book_id, title, author, year, available
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT book_id, title, author, year, available
        FROM Books
        ORDER BY book_id
    """)
    rows = cur.fetchall()

    conn.close()
    return rows


def find_books(title_keyword):
    """
    Finds books by searching the title using a LIKE pattern.
    :param title_keyword: str - keyword to search for inside the title
    :return: list[sqlite3.Row] - list of matching rows containing book_id and title
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT book_id, title
        FROM Books
        WHERE title LIKE ?
        ORDER BY title
    """, (f"%{title_keyword}%",))

    rows = cur.fetchall()
    conn.close()
    return rows


def update_book_availability(book_id, available):
    """
    Updates the availability status of a book (0 = not available, 1 = available).
    :param book_id: int
    :param available: int - must be 0 or 1
    :return: bool - True if updated, False if book_id doesn't exist
    :raises ValueError: if available is not 0 or 1
    """
    if available not in (0, 1):
        raise ValueError("available must be 0 or 1")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE Books
        SET available = ?
        WHERE book_id = ?
    """, (available, book_id))

    conn.commit()
    updated = (cur.rowcount > 0)
    conn.close()
    return updated


def delete_book(book_id):
    """
    Deletes a book from the Books table by its book_id.

    Policy (FIXED):
    - Do NOT delete a book if it has any borrow records (active OR past).
      This prevents breaking history and avoids FK issues.

    :param book_id: int
    :return: bool - True if deleted, False if not deleted (not found or blocked by policy)
    """
    conn = get_connection()
    cur = conn.cursor()

    # Block deletion if there is any borrow history
    cur.execute("""
        SELECT COUNT(*) AS cnt
        FROM Borrow
        WHERE book_id = ?
    """, (book_id,))
    cnt = cur.fetchone()["cnt"]

    if cnt > 0:
        conn.close()
        return False

    cur.execute("""
        DELETE FROM Books
        WHERE book_id = ?
    """, (book_id,))

    conn.commit()
    deleted = (cur.rowcount > 0)
    conn.close()
    return deleted


def available_books():
    """
    Returns a list of all books currently available (available = 1).
    :return: list[sqlite3.Row] - rows containing book_id and title
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT book_id, title
        FROM Books
        WHERE available = 1
        ORDER BY title
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


def books_by_author(author):
    """
    Returns a list of books written by a specific author (exact match).
    :param author: str
    :return: list[sqlite3.Row]
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT book_id, title, author, year, available
        FROM Books
        WHERE author = ?
        ORDER BY year, title
    """, (author,))

    rows = cur.fetchall()
    conn.close()
    return rows


def books_between_years(year_from, year_to):
    """
    Returns books published between two years (inclusive).
    Note: rows with year=NULL will not be returned (SQL behavior).
    :param year_from: int
    :param year_to: int
    :return: list[sqlite3.Row]
    """
    if year_from is None or year_to is None:
        raise ValueError("year_from and year_to must not be None")

    if year_from > year_to:
        year_from, year_to = year_to, year_from

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT book_id, title, author, year, available
        FROM Books
        WHERE year BETWEEN ? AND ?
        ORDER BY year, title
    """, (year_from, year_to))

    rows = cur.fetchall()
    conn.close()
    return rows
