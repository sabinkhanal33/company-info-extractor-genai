# database.py
import os
import psycopg2
from psycopg2 import sql

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"🔴 Error: Could not connect to PostgreSQL database. Please check your .env settings and ensure the database is running.")
        print(f"Details: {e}")
        return None

def create_company_table(conn):
    """Creates the Company_details table if it doesn't already exist."""
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS Company_details (
            id SERIAL PRIMARY KEY,
            company_name VARCHAR(255) NOT NULL,
            founded_in DATE NOT NULL,
            founded_by TEXT[] NOT NULL
        );
        """)
        # Clear the table to ensure fresh data on each run
        cur.execute("TRUNCATE TABLE Company_details RESTART IDENTITY;")
        conn.commit()
    print("✅ Table 'Company_details' is ready.")

def insert_company_data(company_name, founding_date, founders):
    """Inserts a single company record into the database."""
    conn = get_db_connection()
    if not conn:
        return "Database connection failed."
    try:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("""
                INSERT INTO Company_details (company_name, founded_in, founded_by)
                VALUES (%s, %s, %s)
                """),
                (company_name, founding_date, founders)
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
    """Retrieves and prints all records from the Company_details table."""
    conn = get_db_connection()
    if not conn:
        return "Database connection failed."
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, company_name, founded_in, founded_by FROM Company_details ORDER BY id;")
            records = cur.fetchall()
            return records
    except Exception as e:
        return f"Error fetching data: {e}"
    finally:
        if conn:
            conn.close()