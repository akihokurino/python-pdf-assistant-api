SHELL := /bin/bash
PROJECT_ID := liberaworks-dev

vendor:
	source venv/bin/activate && pip install -r requirements.txt

freeze:
	source venv/bin/activate && pip freeze > requirements.txt

update-modules:
	source venv/bin/activate && pip list --outdated --format=json | python -c "import sys, json; [print(pkg['name']) for pkg in json.load(sys.stdin)]" | xargs -n1 pip install -U

types:
	source venv/bin/activate && mypy main.py

run-local:
	source venv/bin/activate && python main.py