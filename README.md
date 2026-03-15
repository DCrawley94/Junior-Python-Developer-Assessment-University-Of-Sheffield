# Junior Python Developer Assessment

> **Environment:** Built and tested on Ubuntu (WSL2) on Windows. The instructions below assume a Linux/macOS environment. If you are on Windows, running inside WSL2 is recommended.
>
> **WSL users:** PostgreSQL does not start automatically on WSL boot. Run the following before any database steps:
> ```bash
> sudo service postgresql start
> ```

## Prerequisites

Ensure the following are installed before getting started:

| Tool | Version used | Notes |
|---|---|---|
| Python | 3.14 | [python.org](https://www.python.org/downloads/) or via pyenv |
| PostgreSQL / psql | 16.13 | [postgresql.org](https://www.postgresql.org/download/) or via package manager|
| Make | Any | Pre-installed on macOS/Linux; Windows users should use WSL2. Can also be installed via package manager|

---

Note: this project uses `make` as a convenience wrapper for common setup commands. All commands shown below are intended to be run in a shell/terminal. If you don't have `make` available you can run the equivalent commands manually (examples below).

Manual equivalents (run in a terminal/shell):

```bash
# create venv and install deps
python -m venv venv
venv/bin/pip install -r requirements-dev.txt

# create databases (requires psql on PATH)
psql -f create_db.sql

# seed the database
venv/bin/python task_01_setup_db.py

# run tests
venv/bin/pytest -vrP
```

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd sheffield_it_services
```

### 2. Install dependencies

```bash
make install
```

This creates a virtual environment at `venv/` and installs all dependencies from `requirements-dev.txt`.

### 3. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your Postgres credentials:

```
DB_HOST=        # leave blank to connect via Unix socket (no password needed)
                # set to localhost to connect via TCP (password required)
DB_PORT=5432
DB_NAME=sheffield_assessment
DB_USER=        # your Postgres username
DB_PASSWORD=    # leave blank if using peer authentication
TEST_DB_NAME=sheffield_assessment_test
```

> **Peer authentication:** If you set up Postgres without a password (e.g. your user was created with `createuser --superuser $USER`), leave `DB_HOST` and `DB_PASSWORD` blank. psycopg2 will connect via Unix socket and no password is required.
>
> If your Postgres requires a password, set `DB_HOST=localhost` and fill in `DB_PASSWORD`.



## Task 1 — Seed the database

Create the databases (if not already present) and populate them with sample Customers and Orders:

```bash
# create the databases
make db

# seed the database
make seed
```

`make db` runs `create_db.sql` and creates both `sheffield_assessment` and `sheffield_assessment_test`.

`make seed` runs `task_01_setup_db.py`, which creates the `customers` and `orders` tables and inserts sample data (30 customers, ~50 orders). Re-running is safe — the script truncates existing data and re-inserts.

Quick verification

```bash
# Count customers using psql (ensure DB env vars are set)
psql -d "$DB_NAME" -c "SELECT COUNT(*) FROM customers;"

# Or a quick Python check inside the venv
venv/bin/python -c "from task_01_setup_db import get_connection; conn=get_connection(); cur=conn.cursor(); cur.execute('SELECT COUNT(*) FROM customers'); print(cur.fetchone()); conn.close()"
```

## Task 2 — Run the API server

Start the FastAPI development server (served by `uvicorn`) using the Makefile convenience target:

```bash
make serve
```

This runs `uvicorn task_02_api:app --reload` inside the project's virtualenv. By default the server binds to `127.0.0.1:8000`. This can be overridden if needed (see example below) but for local testing the default should be fine.

```bash
# Overriding the host and port
make serve DEV_HOST=0.0.0.0 DEV_PORT=8080
```

Endpoints and interactive docs
- Open the automatic Swagger UI at: http://127.0.0.1:8000/docs
- Open the ReDoc docs at: http://127.0.0.1:8000/redoc

Quick curl examples

```bash
# Get customer with id 1
curl http://127.0.0.1:8000/customers/1

# JSON pretty-print
curl http://127.0.0.1:8000/customers/1 | jq
```

Alternatively you can use a tool like Postman.


## Task 3 — Run the ETL script

Run the ETL job using the Makefile convenience target:

```bash
make etl
```

This runs `python task_03_etl.py` inside the project's virtualenv and writes a CSV to `output/export.csv`.

Notes:
- Ensure the database is created and seeded (`make db` / `make seed`) and `.env` is configured.
- The script extracts active customers and their orders, computes `total_value = quantity * unit_price`, and writes the results.

Quick checks

```bash
# Run ETL
make etl

# Inspect the first few lines
head -n 5 output/export.csv
```




