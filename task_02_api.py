"""FastAPI app exposing customer data.

Provides `GET /customers/{customer_id}` returning a customer and their orders.
Run: `uvicorn task_02_api:app --reload` in virtual environment (or `make serve`)
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Generator

from psycopg2.extensions import connection as _Conn

import task_01_setup_db as setup_db

app = FastAPI()


def get_db() -> Generator[_Conn, None, None]:
    """FastAPI dependency that yields a DB connection and closes it.

    Tests can override this dependency to return a shared `db_conn`
    without closing it.
    """
    conn = setup_db.get_connection()
    try:
        yield conn
    finally:
        conn.close()


class Order(BaseModel):
    order_id: int
    product_name: str
    quantity: int
    unit_price: float


class CustomerResponse(BaseModel):
    customer_id: int
    first_name: str
    surname: str
    email: str
    status: str
    orders: list[Order]


class ErrorResponse(BaseModel):
    detail: str


@app.get(
    "/customers/{customer_id}",
    response_model=CustomerResponse,
    responses={
        404: {
            "description": "Customer not found",
            "content": {"application/json": {"schema": ErrorResponse.model_json_schema()}},
        }
    },
)
def get_customer(customer_id: int, conn: _Conn = Depends(get_db)) -> dict:
    """Return a single customer and their orders by customer_id."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT customer_id, first_name, surname, email, status FROM customers WHERE customer_id = %s",
            (customer_id,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Customer not found")

        customer = {
            "customer_id": row[0],
            "first_name": row[1],
            "surname": row[2],
            "email": row[3],
            "status": row[4],
        }

        cur.execute(
            "SELECT order_id, product_name, quantity, unit_price FROM orders WHERE customer_id = %s",
            (customer_id,),
        )
        orders = [
            {
                "order_id": r[0],
                "product_name": r[1],
                "quantity": r[2],
                "unit_price": float(r[3]),
            }
            for r in cur.fetchall()
        ]

        customer["orders"] = orders
        return customer
