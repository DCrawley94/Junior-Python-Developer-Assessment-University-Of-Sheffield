.PHONY: venv install db seed test

venv:
	python -m venv venv

install: venv
	venv/bin/pip install -r requirements-dev.txt

db:
	psql -f create_db.sql

seed: venv
	venv/bin/python task_01_setup_db.py

test: venv
	venv/bin/pytest -vrP
