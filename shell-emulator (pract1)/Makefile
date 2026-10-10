.PHONY: run test lint

run:
	python3 -m src.main

test:
	python3 -m unittest discover -s tests

lint:
	ruff check src tests --line-length 80
