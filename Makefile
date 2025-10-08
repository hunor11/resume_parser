.PHONY: setup dev lint format test run

setup:
	python -m venv backend/.venv
	PYTHONPATH=backend . backend/.venv/bin/activate && pip install --upgrade pip && \
		pip install -r backend/requirements.txt && \
		pip install black ruff mypy pytest httpx pre-commit && \
		pre-commit install

dev:
	PYTHONPATH=backend . backend/.venv/bin/activate && uvicorn app.main:app --reload --app-dir backend

lint:
	PYTHONPATH=backend . backend/.venv/bin/activate && ruff check backend && black --check backend && mypy backend

format:
	PYTHONPATH=backend . backend/.venv/bin/activate && ruff check --fix backend && black backend

test:
	PYTHONPATH=backend . backend/.venv/bin/activate && pytest -q backend/tests

run:
	PYTHONPATH=backend . backend/.venv/bin/activate && uvicorn app.main:app --reload --app-dir backend
