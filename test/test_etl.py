"""Tests for Task 3 - ETL script.

This module tests the ETL pipeline functions implemented in
`task_03_etl.py`.

Fixtures used (from `test/conftest.py` and pytest):

 - `db_conn`: psycopg2 connection to the test database containing the
     seeded sample data; used by `extract()` to query active customers.
 - `tmp_path`: pytest-provided temporary directory used to write and
     validate the CSV output in `export()`.
"""

from task_03_etl import extract, transform, export


def test_extract_returns_only_active_customers(db_conn):
    rows = extract(db_conn)
    assert len(rows) > 0
    assert all(r.get("status") == "active" for r in rows)


def test_transform_concatenates_name():
    sample = [
        {
            "first_name": "John",
            "surname": "Doe",
            "quantity": 2,
            "unit_price": 5.0,
            "order_id": 1,
            "customer_id": 1,
            "product_name": "Widget",
            "email": "john@example.com",
            "status": "active",
        }
    ]
    out = transform(sample)
    assert out[0]["full_name"] == "John Doe"


def test_transform_calculates_total_value():
    sample = [
        {"quantity": 3, "unit_price": 2.5, "first_name": "A", "surname": "B"}
    ]
    out = transform(sample)
    assert out[0]["total_value"] == round(3 * 2.5, 2)


def test_export_creates_csv_file(db_conn, tmp_path):
    rows = extract(db_conn)
    transformed = transform(rows)
    out_file = tmp_path / "export.csv"
    export(transformed, str(out_file))
    assert out_file.exists()
    # sanity check: file contains header + at least one row of data
    text = out_file.read_text()
    assert "order_id" in text
    assert len(text.splitlines()) >= 2
