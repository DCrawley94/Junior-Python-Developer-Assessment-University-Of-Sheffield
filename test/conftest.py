import os

import psycopg2
import pytest
from dotenv import load_dotenv

from task_01_setup_db import get_connection, create_tables

load_dotenv()


@pytest.fixture
def db_conn():
    """Provide a clean test database connection for each test.

    Creates the schema, inserts a small set of known fixed rows,
    yields the connection, then truncates everything on teardown.
    """
    # Use the shared connection helper so test and dev environments behave
    # identically (socket vs TCP handling, port, password). Pass the test DB
    # name so tests connect to the test database.
    conn = get_connection(dbname=os.getenv("TEST_DB_NAME"))
    create_tables(conn)

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO customers (first_name, surname, email, status) VALUES
                ('Jane',  'Smith', 'jane.smith@example.com',  'active'),
                ('Bob',   'Jones', 'bob.jones@example.com',   'archived'),
                ('Alice', 'Brown', 'alice.brown@example.com', 'suspended')
        """)
        cur.execute(
            "SELECT customer_id FROM customers WHERE email = 'jane.smith@example.com'"
        )
        jane_id = cur.fetchone()[0]
        cur.execute(
            """
            INSERT INTO orders (customer_id, product_name, quantity, unit_price)
            VALUES (%s, 'Widget A', 3, 10.00),
                   (%s, 'Gadget Pro', 1, 99.99)
            """,
            (jane_id, jane_id),
        )
    conn.commit()

    yield conn

    with conn.cursor() as cur:
        cur.execute("TRUNCATE customers, orders RESTART IDENTITY CASCADE")
    conn.commit()
    conn.close()