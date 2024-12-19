MAKEFLAGS=--no-builtin-rules --no-builtin-variables --always-make
ROOT := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))
SHELL := /bin/bash
PROJECT_ID := pdf-assistant-445201

vendor:
	source venv/bin/activate && pip install -r requirements.txt

freeze:
	source venv/bin/activate && pip freeze > requirements.txt

update-modules:
	source venv/bin/activate && pip list --outdated --format=json | python -c "import sys, json; [print(pkg['name']) for pkg in json.load(sys.stdin)]" | xargs -n1 pip install -U

types:
	source venv/bin/activate && mypy api.py

run-local:
	source venv/bin/activate && python api.py

gcloud-login:
	gcloud auth application-default login

push-pdf-assistant-api:
	gcloud --quiet config set project $(PROJECT_ID)
	docker build --platform linux/amd64 -t gcr.io/$(PROJECT_ID)/pdf-assistant-api:latest .
	docker push gcr.io/$(PROJECT_ID)/pdf-assistant-api:latest

terraform-plan:
	gcloud config set project $(PROJECT_ID)
	cd terraform && terraform plan

terraform-apply:
	gcloud config set project $(PROJECT_ID)
	cd terraform && terraform apply