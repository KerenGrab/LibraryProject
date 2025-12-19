# LibraryProject
Python-based Library Management System using SQLite3
A modular Python-based Library Management System demonstrating database design, SQL querying, and real-world system modeling using SQLite.

**Library Management System — Python & SQLite**

## Overview
This project is a **Library Management System** implemented in Python using an SQLite database.
The system simulates the core operations of a real-world library, including managing books, users, borrow transactions, and operational reports.

The project was developed as a **learning-focused, end-to-end database application**, with emphasis on:
- database design
- SQL querying
- translating real-world workflows into code
- and building a coherent system from multiple interacting modules.


## Project Motivation

I chose to focus this project specifically on the **database domain**, as it is an area that strongly interests me and one I wanted to explore beyond theoretical coursework.
Since I had no prior hands-on experience with SQLite or Python’s sqlite3 module, I intentionally selected a project that would require learning a new technology while building something practical and realistic. A library system was a natural choice, as it involves structured data, relationships between entities, and meaningful real-world use cases.


## Learning Process & Development Journey
This project was built iteratively, with each stage introducing new concepts and challenges.

### 1. Initial Learning Phase – SQLite & Basic Queries
- Learned SQLite from scratch using online research, documentation, and tutorial videos.
- Explored how to create databases, tables, and execute basic SQL queries from Python.
- Practiced running queries through PyCharm Community Edition using sqlite3.

Key learning:
Understanding how Python code interacts with a persistent database, rather than in-memory data structures.

### 2. Expanding from Queries to Use Cases
After writing basic queries (e.g., retrieving all books), I began thinking in terms of **use cases**:

- Searching books by author
- Filtering by publication year ranges
- Checking book availability
- Supporting queries that would actually be useful for library staff

This marked a shift from *“writing SQL”* to *“designing functionality.”*

### 3. System Design Based on Real Library Logic

Before implementing modules, I analyzed how a real library operates:
- What actions do library staff perform?
- What data must be tracked?
- What problems might occur during daily operations?

From this analysis, I derived the required functionalities and only then implemented them.
This approach ensured that the database structure and queries served real operational needs.


### 4. Users Module – Staff ↔ User Interactions
The Users module was designed around interactions between library staff and library members, including:

- Creating, searching, and deleting users
- Tracking how many books a user has borrowed
- Listing borrowed books per user
- Calculating accumulated debt due to late returns

While implementing this module, I learned the importance of **Primary Keys and unique identifiers**:

- User lookup is performed via unique IDs rather than names
- This prevents ambiguity and data inconsistencies


### 5. Borrow Module – Increased Query Complexity

The Borrow (Loans) module introduced higher logical complexity:

- Active borrows vs. returned borrows
- Borrow history per user
- Cross-table relationships between users, books, and borrow records

The main challenge here was **translating conceptual questions into SQL queries**, and then embedding those queries correctly into Python functions.

This was the point where I moved from *writing code* to *thinking in SQL*.


### 6. Reports Module – Operational & Management Perspective

In the Reports module, the technical difficulty decreased, but the **conceptual difficulty increased**.

The challenge was identifying:

- What information library staff need on a daily basis
- What summaries are useful for managers
- Which histories and statistics should appear in periodic or annual reports

This required thinking from an **operational and managerial perspective**, not just as a developer.


### 7. Main Module – System Orchestration

After completing all core modules, I implemented the `main` file, which acts as the **entry point and control center** of the system.

At this stage, I focused on:

- Connecting all modules into a single workflow
- Handling success and failure scenarios
- Running test flows to validate system behavior
- Observing outputs to verify correctness and completeness

This step transformed the project from a collection of modules into a **fully functioning system**.


## System Architecture

The project consists of six main files:

- **database.py**
  Handles database connection and initialization.

- **books.py**
  Manages book-related operations such as availability and retrieval.

- **users.py**
  Manages library users and their associated data.

- **borrow.py**
  Handles borrowing logic, active loans, and borrow history.

- **reports.py**
  Generates summaries and operational reports for staff and management.

- **main.py**
  The system entry point that coordinates all modules and executes workflows.


## Functional Capabilities

The system supports:

- Managing books and tracking availability
- Managing users and their borrowing activity
- Recording borrow and return transactions
- Tracking historical data
- Producing operational and management-oriented reports
- Handling expected failure cases (e.g., unavailable books, missing users)

The design prioritizes **clarity, correctness, and realistic workflows** over UI or performance optimization.


## Key Skills & Concepts Demonstrated

- Python programming
- SQLite database design
- SQL querying (including joins and filtering)
- Data integrity via primary keys
- Modular system design
- Translating real-world processes into software
- Iterative development and reflective learning


## Future Extensions

While this project focuses on core functionality, it was designed in a way that allows future extensions such as:

- More advanced reporting
- User roles and permissions
- Enhanced validation and testing
- UI or web-based interface


## Summary

This project represents a complete learning journey from first contact with SQLite to building a multi-module database-driven system.
It demonstrates not only technical implementation, but also **system thinking, problem analysis, and real-world applicability**.
