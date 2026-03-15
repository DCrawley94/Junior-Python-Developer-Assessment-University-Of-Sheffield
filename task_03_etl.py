# Task 3 - ETL Script
#
# A standalone script intended to be run on a schedule (e.g. cron job).
# Reads directly from the database and writes results to output/export.csv.
#
# Steps:
#   1. Extract  - query all *active* customers and their orders
#   2. Transform - full_name = first_name + " " + surname
#                  total_value = quantity * unit_price
#   3. Export   - write results to output/export.csv
#
# Run with: python etl.py

import csv
import os
from typing import List, Dict, Optional

from psycopg2.extensions import connection as _Conn

import task_01_setup_db as setup_db


def get_connection(dbname: Optional[str] = None) -> _Conn:
    """Return a psycopg2 connection to the database (wrapper around setup helper)."""
    return setup_db.get_connection(dbname=dbname)


def extract(conn: _Conn) -> List[Dict]:
    """Query the DB and return active customers with their orders as a list of dicts.

    Each dict represents one order row joined with the customer fields.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                customers.customer_id,
                customers.first_name,
                customers.surname,
                customers.email,
                customers.status,
                orders.order_id,
                orders.product_name,
                orders.quantity,
                orders.unit_price
            FROM customers
            JOIN orders ON orders.customer_id = customers.customer_id
            WHERE customers.status = 'active'
            """
        )
        cols = [c.name for c in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    return rows


def transform(rows: List[Dict]) -> List[Dict]:
    """Add `full_name` and `total_value` to each row and normalize numeric types."""
    out = []
    for r in rows:
        quantity = int(r.get("quantity", 0))
        unit_price = float(r.get("unit_price", 0.0))
        first = (r.get("first_name") or "").strip()
        surname = (r.get("surname") or "").strip()
        r["full_name"] = " ".join(p for p in (first, surname) if p)
        r["quantity"] = quantity
        r["unit_price"] = round(unit_price, 2)
        r["total_value"] = round(quantity * unit_price, 2)
        out.append(r)
    return out


def export(data: List[Dict], output_path: str = "output/export.csv"):
    """Write the transformed data to a CSV file with a predictable header."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fieldnames = [
        "order_id",
        "customer_id",
        "full_name",
        "email",
        "product_name",
        "quantity",
        "unit_price",
        "total_value",
    ]
    with open(output_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            out = {k: row.get(k) for k in fieldnames}
            writer.writerow(out)


if __name__ == "__main__":
    conn = get_connection()
    raw = extract(conn)
    conn.close()
    transformed = transform(raw)
    export(transformed)
    print("ETL complete. Output written to output/export.csv")
