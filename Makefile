.PHONY: install, run, debug, clean, fclean, lint, lint-strict

.venv/.installed:
	python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" || \
		(echo "Please, install Python 3.10+ before any run."; exit 1)
	python3 -m venv .venv
	.venv/bin/python3 -m pip install -r requirements.txt
	touch .venv/.installed

install: .venv/.installed

run: install
	.venv/bin/python3 main.py

debug: install
	.venv/bin/python3 -m pdb main.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

fclean: clean
	find . -type d -name ".venv" -exec rm -rf {} +

lint: 
	.venv/bin/flake8 . --exclude .venv
	.venv/bin/mypy . --warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	.venv/bin/flake8 . --exclude .venv
	.venv/bin/mypy . --strict
