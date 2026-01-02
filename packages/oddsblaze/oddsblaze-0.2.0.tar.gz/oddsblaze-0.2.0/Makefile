.PHONY: docs docs-live docs-clean

docs:
	uv run --group docs mkdocs build --clean

docs-live:
	uv run --group docs mkdocs serve --dev-addr 0.0.0.0:8000

docs-clean:
	rm -rf site