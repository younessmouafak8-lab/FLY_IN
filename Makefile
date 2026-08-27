MAP = maps/easy/01_linear_path.txt

install:
	poetry install
run:
	@poetry run python3 main.py $(MAP)
 
debug:
	@poetry run python3 -m pdb main.py
 
clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -rf .mypy_cache
 
lint:
	@poetry run flake8 .
	@poetry run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs