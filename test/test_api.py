"""Tests for Task 2 - REST API.

This module contains functional tests for the `/customers/{customer_id}`
endpoint. Tests rely on fixtures defined in `test/conftest.py`:

 - `db_conn`: provides a psycopg2 connection to the test database with
   a small set of seeded rows.
 - `test_client`: a FastAPI `TestClient` configured to use the test DB
   connection so HTTP requests exercise the same data.

Tests are written to be deterministic and rely on the fixed data inserted
by the `db_conn` fixture (Jane/Bob/Alice).
"""


def test_get_customer_returns_200(test_client, db_conn):
	"""A valid customer_id should return a 200 response."""
	with db_conn.cursor() as cur:
		cur.execute("SELECT customer_id FROM customers WHERE email = %s", ("jane.smith@example.com",))
		jane_id = cur.fetchone()[0]

	resp = test_client.get(f"/customers/{jane_id}")
	assert resp.status_code == 200


def test_get_customer_returns_correct_data(test_client, db_conn):
	"""Response body should contain the expected customer fields and orders."""
	with db_conn.cursor() as cur:
		cur.execute("SELECT customer_id FROM customers WHERE email = %s", ("jane.smith@example.com",))
		jane_id = cur.fetchone()[0]

	resp = test_client.get(f"/customers/{jane_id}")
	assert resp.status_code == 200
	body = resp.json()
	assert body["first_name"] == "Jane"
	assert body["surname"] == "Smith"
	assert isinstance(body.get("orders"), list)
	assert len(body["orders"]) >= 2


def test_get_customer_unknown_id_returns_404(test_client):
	"""A customer_id that doesn't exist should return 404."""
	resp = test_client.get("/customers/999999")
	assert resp.status_code == 404
