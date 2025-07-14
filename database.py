# database.py (SQLite version)
import sqlite3

# No need for .env or os imports for SQLite

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect("companies.db")
        return conn
    except sqlite3.Error as e:
        print(f"🔴 Error: Could not connect to SQLite database.")
        print(f"Details: {e}")
        return None

def create_company_table(conn):
    """Creates the Company_details table if it doesn't already exist (SQLite)."""
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Company_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            founded_in TEXT NOT NULL,
            founded_by TEXT NOT NULL
        );
    """)
    # Clear the table to ensure fresh data on each run
    cur.execute("DELETE FROM Company_details;")
    conn.commit()
    print("✅ Table 'Company_details' is ready.")

def insert_company_data(company_name, founding_date, founders):
    """Inserts a single company record into the SQLite database."""
    conn = get_db_connection()
    if not conn:
        return "Database connection failed."
    try:
        cur = conn.cursor()
        founders_str = ", ".join(founders) if isinstance(founders, list) else str(founders)
        cur.execute(
            """
            INSERT INTO Company_details (company_name, founded_in, founded_by)
            VALUES (?, ?, ?)
            """,
            (company_name, str(founding_date), founders_str)
        )
        conn.commit()
        return f"Successfully added {company_name} to the database."
    except Exception as e:
        conn.rollback()
        return f"Error inserting data for {company_name}: {e}"
    finally:
        if conn:
            conn.close()

def get_all_companies():
    """Retrieves and prints all records from the Company_details table (SQLite)."""
    conn = get_db_connection()
    if not conn:
        return "Database connection failed."
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, company_name, founded_in, founded_by FROM Company_details ORDER BY id;")
        records = cur.fetchall()
        return records
    except Exception as e:
        return f"Error fetching data: {e}"
    finally:
        if conn:
            conn.close()
