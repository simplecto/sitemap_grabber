.PHONY: help
help:
	@echo "Usage: make [target]"
	@echo "Targets:"
	@echo "  test       Run tests"

.PHONY: test
test:
	@echo "Running tests..."
	python -m unittest discover tests/
