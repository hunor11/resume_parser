.PHONY: setup_server setup_frontend dev lint format run_server run_frontend

setup_server:
	python -m venv backend/.venv
	PYTHONPATH=backend . backend/.venv/bin/activate && pip install --upgrade pip && \
		pip install -r backend/requirements.txt && \
		pip install black ruff mypy pytest httpx pre-commit && \
		pre-commit install

setup_frontend:
	cd frontend && npm install

lint:
	PYTHONPATH=backend . backend/.venv/bin/activate && ruff check backend && black --check backend && mypy backend

format:
	PYTHONPATH=backend . backend/.venv/bin/activate && ruff check --fix backend && black backend

run_server:
	PYTHONPATH=backend . backend/.venv/bin/activate && uvicorn app.main:app --reload --app-dir backend

run_frontend:
	cd frontend && npm run dev
