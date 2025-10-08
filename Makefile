.PHONY: setup dev lint format test run

setup:
	python -m venv backend/.venv
	. backend/.venv/bin/activate && pip install --upgrade pip && \
		pip install -r backend/requirements.txt && \
		pip install black ruff mypy pytest httpx pre-commit && \
		pre-commit install

dev:
	. backend/venv/bin/activate && uvicorn app.main:app --reload --app-dir backend

lint:
	. backend/venv/bin/activate && ruff check backend && black --check backend && mypy backend

format:
	. backend/venv/bin/activate && ruff check --fix backend && black backend

test:
	PYTHONPATH=backend . backend/venv/bin/activate && pytest -q backend/tests

run:
	. backend/venv/bin/activate && uvicorn app.main:app --reload --app-dir backend
