from db import get_connection

"""
Reports module.

This module contains READ-ONLY database queries that generate reports,
summaries, and historical views of the library system.

Design principles:
- This file must NOT modify the database.
- No INSERT / UPDATE / DELETE operations are allowed here.
- The purpose of this module is to present information for monitoring,
  reporting, and documentation purposes.
"""


# ==================================================
# General / Global Reports
# ==================================================

def full_books_catalog():
    """
    Returns the complete books catalog of the library.

    This report includes:
    - All books that currently exist in the system
    - Both available and unavailable books
    - All historical book entries (each row represents a physical copy)

    This function does NOT filter by availability.

    :return: list[sqlite3.Row]
        Each row contains:
        - book_id
        - title
        - author
        - year
        - available
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            book_id,
            title,
            author,
            year,
            available
        FROM Books
        ORDER BY title, book_id
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


def full_users_list():
    """
    Returns a list of all users registered in the library system.

    This report represents the complete users registry,
    regardless of whether users have borrowed books or not.

    :return: list[sqlite3.Row]
        Each row contains:
        - user_id
        - name
        - phone
        - email
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            user_id,
            name,
            phone,
            email
        FROM Users
        ORDER BY name
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


def full_borrow_history():
    """
    Returns the complete borrow history of the library.

    This includes:
    - Active borrows
    - Returned borrows
    - Historical borrowing records

    The result joins Users, Books, and Borrow to provide
    a full contextual view of each borrow operation.

    :return: list[sqlite3.Row]
        Each row contains:
        - borrow_id
        - borrow_date
        - return_date
        - book_id
        - book title and author
        - user_id
        - user name, phone, email
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            b.borrow_id,
            b.borrow_date,
            b.return_date,
            bk.book_id,
            bk.title,
            bk.author,
            u.user_id,
            u.name,
            u.phone,
            u.email
        FROM Borrow AS b
        JOIN Books  AS bk ON bk.book_id = b.book_id
        JOIN Users  AS u  ON u.user_id  = b.user_id
        ORDER BY b.borrow_date DESC
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


# ==================================================
# Current State Reports
# ==================================================

def currently_available_books():
    """
    Returns all books that are currently available for borrowing.

    This report reflects the real-time availability state
    of the library inventory.

    :return: list[sqlite3.Row]
        Each row contains:
        - book_id
        - title
        - author
        - year
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            book_id,
            title,
            author,
            year
        FROM Books
        WHERE available = 1
        ORDER BY title
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


def currently_borrowed_books():
    """
    Returns all books that are currently borrowed (active borrows).

    This report includes:
    - Book details
    - User details
    - Borrow date

    Only borrows with return_date IS NULL are included.

    :return: list[sqlite3.Row]
        Each row contains:
        - borrow_id
        - book_id
        - book title and author
        - user_id
        - user name
        - borrow_date
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            b.borrow_id,
            bk.book_id,
            bk.title,
            bk.author,
            u.user_id,
            u.name,
            b.borrow_date
        FROM Borrow AS b
        JOIN Books  AS bk ON bk.book_id = b.book_id
        JOIN Users  AS u  ON u.user_id = b.user_id
        WHERE b.return_date IS NULL
        ORDER BY b.borrow_date DESC
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


def users_with_active_borrows():
    """
    Returns all users who currently have at least one active borrow.

    Each user appears only once, even if they have multiple borrowed books.

    :return: list[sqlite3.Row]
        Each row contains:
        - user_id
        - name
        - phone
        - email
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT
            u.user_id,
            u.name,
            u.phone,
            u.email
        FROM Borrow AS b
        JOIN Users AS u ON u.user_id = b.user_id
        WHERE b.return_date IS NULL
        ORDER BY u.name
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


# ==================================================
# Book-focused Reports
# ==================================================

def borrow_history_of_book(book_id):
    """
    Returns the full borrow history of a specific book copy.

    This includes:
    - All users who borrowed the book
    - Borrow and return dates
    - Both active and completed borrows

    :param book_id: int
        The ID of the specific book copy (Books.book_id)

    :return: list[sqlite3.Row]
        Each row contains:
        - borrow_id
        - borrow_date
        - return_date
        - user_id
        - user name, phone, email
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            b.borrow_id,
            b.borrow_date,
            b.return_date,
            u.user_id,
            u.name,
            u.phone,
            u.email
        FROM Borrow AS b
        JOIN Users AS u ON u.user_id = b.user_id
        WHERE b.book_id = ?
        ORDER BY b.borrow_date DESC
    """, (book_id,))

    rows = cur.fetchall()
    conn.close()
    return rows


def most_borrowed_books():
    """
    Returns books ordered by total number of times they were borrowed.

    Books are grouped by logical book identity (title + author),
    not by individual copy.

    This report is useful for popularity analysis.

    :return: list[sqlite3.Row]
        Each row contains:
        - title
        - author
        - borrow_count
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            bk.title,
            bk.author,
            COUNT(b.borrow_id) AS borrow_count
        FROM Borrow AS b
        JOIN Books AS bk ON bk.book_id = b.book_id
        GROUP BY bk.title, bk.author
        ORDER BY borrow_count DESC
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


# ==================================================
# User-focused Reports
# ==================================================

def borrow_history_of_user(user_id):
    """
    Returns the complete borrowing history of a specific user.

    This includes:
    - Active borrows
    - Returned borrows
    - Book details for each borrow

    :param user_id: int
        The ID of the user

    :return: list[sqlite3.Row]
        Each row contains:
        - borrow_id
        - borrow_date
        - return_date
        - book_id
        - book title and author
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            b.borrow_id,
            b.borrow_date,
            b.return_date,
            bk.book_id,
            bk.title,
            bk.author
        FROM Borrow AS b
        JOIN Books AS bk ON bk.book_id = b.book_id
        WHERE b.user_id = ?
        ORDER BY b.borrow_date DESC
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()
    return rows


def users_by_borrow_count():
    """
    Returns users ordered by the total number of books they borrowed.

    Users with no borrows are included with a borrow count of 0.

    :return: list[sqlite3.Row]
        Each row contains:
        - user_id
        - name
        - borrow_count
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            u.user_id,
            u.name,
            COUNT(b.borrow_id) AS borrow_count
        FROM Users AS u
        LEFT JOIN Borrow AS b ON b.user_id = u.user_id
        GROUP BY u.user_id, u.name
        ORDER BY borrow_count DESC
    """)

    rows = cur.fetchall()
    conn.close()
    return rows
