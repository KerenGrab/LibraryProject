import sqlite3

"""
Database setup for the Library Project.

Tables:
- Books  : each row is a single copy of a book (duplicates allowed intentionally).
- Users  : library members.
- Borrow : connects a user to a specific book copy (book_id) with borrow/return dates.
"""

DB_NAME = "library.db"


def get_connection():
    """
    Opens a connection to the SQLite database and enables foreign key enforcement.
    Returns a connection with sqlite3.Row rows.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

    # IMPORTANT: SQLite does NOT enforce foreign keys unless this is enabled per-connection.
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """
    Creates tables if they don't exist.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Books table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Books (
            book_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            title     TEXT NOT NULL,
            author    TEXT NOT NULL,
            year      INTEGER,
            available INTEGER NOT NULL DEFAULT 1
        );
    """)

    # Users table (FIXED: added phone column to match the code)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL,
            phone   TEXT,
            email   TEXT UNIQUE
        );
    """)

    # Borrow table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Borrow (
            borrow_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id     INTEGER NOT NULL,
            user_id     INTEGER NOT NULL,
            borrow_date TEXT NOT NULL,
            return_date TEXT,
            FOREIGN KEY(book_id) REFERENCES Books(book_id),
            FOREIGN KEY(user_id) REFERENCES Users(user_id)
        );
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized.")
