"""Create DB schema and seed sample Customers/Orders.

Creates `customers` and `orders` tables and populates them with Faker data.
Run: `python task_01_setup_db.py` in virtual environment (or `make seed`).
"""

import os
import random
from typing import Optional

import psycopg2
from psycopg2.extensions import connection as _Conn
from dotenv import load_dotenv
from faker import Faker

load_dotenv()

fake = Faker()

STATUSES = ["active", "archived", "suspended"]
PRODUCTS = [
    "Widget A", "Widget B", "Gadget Pro",
    "Budget Kit", "Deluxe Pack", "Starter Set",
]


def get_connection(dbname: Optional[str] = None) -> _Conn:
    """Return a psycopg2 connection. Uses DB_NAME from .env unless overridden.

    DB_HOST is optional — omitting it causes psycopg2 to connect via Unix
    socket, which works with peer authentication (no password required).
    Set DB_HOST=localhost to connect via TCP instead (password required).
    """
    params = {
        "dbname": dbname or os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }
    host = os.getenv("DB_HOST")
    if host:
        params["host"] = host
        params["port"] = os.getenv("DB_PORT", 5432)
    return psycopg2.connect(**params)


def create_tables(conn: _Conn) -> None:
    """Create customers and orders tables if they do not already exist."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id SERIAL PRIMARY KEY,
                first_name  VARCHAR(100) NOT NULL,
                surname     VARCHAR(100) NOT NULL,
                email       VARCHAR(255) UNIQUE NOT NULL,
                status      VARCHAR(20)  NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id     SERIAL PRIMARY KEY,
                customer_id  INTEGER NOT NULL REFERENCES customers(customer_id),
                product_name VARCHAR(200) NOT NULL,
                quantity     INTEGER NOT NULL,
                unit_price   NUMERIC(10, 2) NOT NULL
            )
        """)
    conn.commit()


def seed_data(conn: _Conn) -> None:
    """Truncate tables and re-populate with Faker-generated sample data.

    Guarantees:
    - Exactly 10 customers per status (active / archived / suspended)
    - Every customer has at least 1 order, ensuring Task 2 always returns
      meaningful data and Task 3 always produces output for active customers
    """
    with conn.cursor() as cur:
        cur.execute("TRUNCATE customers, orders RESTART IDENTITY CASCADE")

        # Cycle through statuses so we get exactly 10 of each across 30 customers
        statuses = [s for s in STATUSES for _ in range(10)]
        customers = [
            (
                fake.first_name(),
                fake.last_name(),
                fake.unique.email(),
                statuses[i],
            )
            for i in range(30)
        ]
        cur.executemany(
            """
            INSERT INTO customers (first_name, surname, email, status)
            VALUES (%s, %s, %s, %s)
            """,
            customers,
        )

        cur.execute("SELECT customer_id FROM customers")
        customer_ids = [row[0] for row in cur.fetchall()]

        # Give every customer at least 1 order, then distribute 20 more randomly
        guaranteed = [
            (
                cid,
                random.choice(PRODUCTS),
                random.randint(1, 10),
                round(random.uniform(5.0, 200.0), 2),
            )
            for cid in customer_ids
        ]
        extra = [
            (
                random.choice(customer_ids),
                random.choice(PRODUCTS),
                random.randint(1, 10),
                round(random.uniform(5.0, 200.0), 2),
            )
            for _ in range(20)
        ]
        cur.executemany(
            """
            INSERT INTO orders (customer_id, product_name, quantity, unit_price)
            VALUES (%s, %s, %s, %s)
            """,
            guaranteed + extra,
        )

    conn.commit()


if __name__ == "__main__":
    conn = get_connection()
    create_tables(conn)
    seed_data(conn)
    conn.close()
    print("Database setup complete.")

