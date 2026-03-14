from task_01_setup_db import seed_data


def test_customers_table_exists(db_conn):
    """customers table should exist after create_tables()."""
    with db_conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'customers'
            )
        """)
        assert cur.fetchone()[0] is True


def test_orders_table_exists(db_conn):
    """orders table should exist after create_tables()."""
    with db_conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'orders'
            )
        """)
        assert cur.fetchone()[0] is True


def test_seed_data_populates_customers(db_conn):
    """seed_data() should insert rows into customers."""
    seed_data(db_conn)
    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM customers")
        assert cur.fetchone()[0] > 0


def test_seed_data_populates_orders(db_conn):
    """seed_data() should insert rows into orders."""
    seed_data(db_conn)
    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM orders")
        assert cur.fetchone()[0] > 0


def test_seed_data_is_idempotent(db_conn):
    """Running seed_data() twice should produce the same row count, not double it."""
    seed_data(db_conn)
    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM customers")
        count_first = cur.fetchone()[0]

    seed_data(db_conn)
    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM customers")
        count_second = cur.fetchone()[0]

    assert count_first == count_second


def test_customer_status_values_are_valid(db_conn):
    """Every customer status should be one of the three allowed values."""
    seed_data(db_conn)
    with db_conn.cursor() as cur:
        cur.execute("SELECT DISTINCT status FROM customers")
        statuses = {row[0] for row in cur.fetchall()}
    assert statuses.issubset({"active", "archived", "suspended"})


def test_customer_rows_have_no_null_required_fields(db_conn):
    """first_name, surname, email, and status must all be populated."""
    seed_data(db_conn)
    with db_conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM customers
            WHERE first_name IS NULL
               OR surname IS NULL
               OR email IS NULL
               OR status IS NULL
        """)
        assert cur.fetchone()[0] == 0


def test_order_rows_have_positive_quantity_and_price(db_conn):
    """Every order must have quantity > 0 and unit_price > 0."""
    seed_data(db_conn)
    with db_conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM orders
            WHERE quantity <= 0 OR unit_price <= 0
        """)
        assert cur.fetchone()[0] == 0


def test_all_orders_reference_valid_customers(db_conn):
    """Every order's customer_id must exist in the customers table."""
    seed_data(db_conn)
    with db_conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.customer_id
            WHERE c.customer_id IS NULL
        """)
        assert cur.fetchone()[0] == 0
