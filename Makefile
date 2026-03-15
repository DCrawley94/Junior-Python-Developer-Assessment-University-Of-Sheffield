.PHONY: venv install db seed test etl

DEV_HOST ?= 127.0.0.1
DEV_PORT ?= 8000

venv:
	python -m venv venv

install: venv
	venv/bin/pip install -r requirements-dev.txt

db:
	psql -f create_db.sql

seed: venv
	venv/bin/python task_01_setup_db.py

K ?=

test: venv
	if [ -n "$(K)" ]; then \
		venv/bin/pytest -vrP -k "$(K)"; \
	else \
		venv/bin/pytest -vrP; \
	fi

serve: venv
	venv/bin/uvicorn task_02_api:app --reload --host $(DEV_HOST) --port $(DEV_PORT)


etl: venv
	venv/bin/python task_03_etl.py
