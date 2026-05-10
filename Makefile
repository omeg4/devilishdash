.PHONY: data preview render lint test clean

data:
	uv run python -m data.ingest.run_all

preview:
	quarto preview

render:
	quarto render

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest

clean:
	rm -rf _site .quarto data/cache
