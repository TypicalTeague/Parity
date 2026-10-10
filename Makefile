.PHONY: backend-check frontend-check contracts-check check

backend-check:
	python -m ruff check backend
	python -m ruff format --check backend
	python -m mypy --config-file backend/pyproject.toml backend/src
	python -m pytest backend/tests

frontend-check:
	npm --prefix frontend run format:check
	npm --prefix frontend run lint
	npm --prefix frontend run typecheck
	npm --prefix frontend run test:run
	npm --prefix frontend run build

contracts-check:
	python -m parity.tools.export_openapi --check contracts/openapi.json
	npm --prefix frontend run contract:check

check: backend-check frontend-check contracts-check
