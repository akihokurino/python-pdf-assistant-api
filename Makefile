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
	source venv/bin/activate && mypy entrypoint/api.py
	source venv/bin/activate && mypy entrypoint/clean_openai_assistant.py

test:
	source venv/bin/activate && pytest

run-api:
	source venv/bin/activate && PROJECT_ID=$(PROJECT_ID) IS_LOCAL=true python -m entrypoint.api

run-clean-openai-assistant:
	source venv/bin/activate && PROJECT_ID=$(PROJECT_ID) IS_LOCAL=true python -m entrypoint.clean_openai_assistant

gcloud-login:
	gcloud auth application-default login

push-pdf-assistant:
	gcloud --quiet config set project $(PROJECT_ID)
	docker build --platform linux/amd64 -t gcr.io/$(PROJECT_ID)/pdf-assistant:latest .
	docker push gcr.io/$(PROJECT_ID)/pdf-assistant:latest

deploy: push-pdf-assistant
	gcloud run deploy api \
      	--image gcr.io/$(PROJECT_ID)/pdf-assistant:latest \
      	--add-cloudsql-instances $(PROJECT_ID):asia-northeast1:app \
      	--region asia-northeast1 \
      	--cpu 1000m \
        --memory 512Mi \
        --port 8080 \
      	--platform managed \
      	--no-allow-unauthenticated \
      	--service-account cloud-run-sa@pdf-assistant-445201.iam.gserviceaccount.com \
      	--set-env-vars PROJECT_ID=$(PROJECT_ID) \
      	--ingress all \
      	--command "sh" \
      	--args "-c,python -m entrypoint.api"

	gcloud run jobs deploy clean-openai-assistant \
        --image gcr.io/$(PROJECT_ID)/pdf-assistant:latest \
        --set-cloudsql-instances $(PROJECT_ID):asia-northeast1:app \
        --region asia-northeast1 \
        --cpu 1000m \
        --memory 512Mi \
        --service-account cloud-run-sa@pdf-assistant-445201.iam.gserviceaccount.com \
        --set-env-vars PROJECT_ID=$(PROJECT_ID) \
        --max-retries 0 \
        --parallelism 1 \
        --tasks 1 \
        --command "sh" \
        --args "-c,python -m entrypoint.clean_openai_assistant"

terraform-plan:
	gcloud config set project $(PROJECT_ID)
	cd terraform && terraform plan

terraform-apply:
	gcloud config set project $(PROJECT_ID)
	cd terraform && terraform apply

clean-docker:
	docker system prune -a -f

connect-cloud-sql:
	./cloud_sql/proxy $(PROJECT_ID):asia-northeast1:app