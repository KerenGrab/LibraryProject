"""
Main entry point for the Library Management System.

This file demonstrates a complete and valid usage flow of the system:
- Database initialization
- Creating books and users
- Borrowing and returning books
- Displaying system state and reports

Important design notes:
- This file contains NO business logic.
- All actions are performed by calling functions from other modules.
- This file serves as a runnable demo that proves the system works end-to-end.
"""

from db import init_db
from books import add_book, list_books, available_books
from users import create_user, list_users, borrowed_books_of_user
from borrow import borrow_book, return_book, list_active_borrows
from reports import (
    full_borrow_history,
    currently_available_books,
    most_borrowed_books
)


def print_rows(title, rows):
    """
    Utility function for printing query results in a readable format.

    :param title: str - title printed above the rows
    :param rows: iterable of sqlite3.Row
    """
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    if not rows:
        print("(no rows)")
        return

    for row in rows:
        print(dict(row))


def main():
    # ==================================================
    # 1) System setup
    # ==================================================
    init_db()
    print("Database initialized and ready.")

    # ==================================================
    # 2) Create initial data (books & users)
    # ==================================================
    b1 = add_book("Harry Potter", "J.K. Rowling", 1997)
    b2 = add_book("Harry Potter", "J.K. Rowling", 1997)  # second copy
    b3 = add_book("Clean Code", "Robert C. Martin", 2008)

    print(f"Books added: {b1}, {b2}, {b3}")

    u1 = create_user("Alice Cohen", phone="050-1111111", email="alice@example.com")
    u2 = create_user("Bob Levi", phone="052-2222222", email="bob@example.com")

    print(f"Users created: {u1}, {u2}")

    # ==================================================
    # 3) Initial state reports
    # ==================================================
    print_rows("All books in the system:", list_books())
    print_rows("Currently available books:", available_books())

    # ==================================================
    # 4) Borrowing flow (including intentional failure)
    # ==================================================
    borrow_id_1 = borrow_book(u1, b1, "2025-12-19")
    print(f"\nBorrow attempt: user {u1} -> book {b1} => borrow_id = {borrow_id_1}")

    # This borrow should fail because the same copy is already borrowed
    borrow_fail = borrow_book(u2, b1, "2025-12-19")
    print(f"Borrow same copy again (expected failure): {borrow_fail}")

    # Borrowing a different copy should succeed
    borrow_id_2 = borrow_book(u2, b2, "2025-12-19")
    print(f"Borrow different copy: user {u2} -> book {b2} => borrow_id = {borrow_id_2}")

    # ==================================================
    # 5) State while borrows are active
    # ==================================================
    print_rows("Active borrows:", list_active_borrows())
    print_rows(
        f"Active borrows of user {u1}:",
        borrowed_books_of_user(u1, active_only=True)
    )
    print_rows(
        f"Active borrows of user {u2}:",
        borrowed_books_of_user(u2, active_only=True)
    )

    # ==================================================
    # 6) Return flow (including intentional failure)
    # ==================================================
    returned = return_book(borrow_id_1, "2025-12-20")
    print(f"\nReturn borrow_id {borrow_id_1} => {returned}")

    # Returning the same borrow again should fail
    returned_again = return_book(borrow_id_1, "2025-12-21")
    print(f"Return same borrow again (expected failure) => {returned_again}")

    # ==================================================
    # 7) Reports after return
    # ==================================================
    print_rows("Available books after return:", currently_available_books())
    print_rows("Full borrow history:", full_borrow_history())
    print_rows("Most borrowed books:", most_borrowed_books())

    # ==================================================
    # 8) Final users list
    # ==================================================
    print_rows("All users in the system:", list_users())


if __name__ == "__main__":
    main()
