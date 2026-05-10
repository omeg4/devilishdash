QUARTO_BIN := $(HOME)/.local/share/quarto/bin
VENV_PYTHON := $(shell uv run python -c "import sys; print(sys.executable)")

.PHONY: data preview render lint test clean

data:
	uv run python -m data.ingest.run_all

preview:
	PATH="$(QUARTO_BIN):$$PATH" QUARTO_PYTHON="$(VENV_PYTHON)" uv run quarto preview

render:
	PATH="$(QUARTO_BIN):$$PATH" QUARTO_PYTHON="$(VENV_PYTHON)" uv run quarto render

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest

clean:
	rm -rf _site .quarto data/cache
