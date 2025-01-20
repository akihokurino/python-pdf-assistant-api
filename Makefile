MAKEFLAGS=--no-builtin-rules --no-builtin-variables --always-make
ROOT := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))
SHELL := /bin/bash
PROJECT_ID := my-python-448116

vendor:
	source venv/bin/activate && poetry install

update-modules:
	source venv/bin/activate && poetry update

types:
	source venv/bin/activate && mypy .

test:
	source venv/bin/activate && pytest

run-api:
	source venv/bin/activate && PROJECT_ID=$(PROJECT_ID) IS_LOCAL=true python -m entrypoint.api

run-clean-openai-assistant:
	source venv/bin/activate && PROJECT_ID=$(PROJECT_ID) IS_LOCAL=true python -m entrypoint.clean_openai_assistant

gcloud-login:
	gcloud --quiet config set project $(PROJECT_ID)
	gcloud auth application-default login

push-pdf-assistant:
	gcloud --quiet config set project $(PROJECT_ID)
	docker build --platform linux/amd64 -t asia-northeast1-docker.pkg.dev/$(PROJECT_ID)/app/pdf-assistant:latest .
	gcloud auth configure-docker asia-northeast1-docker.pkg.dev
	docker push asia-northeast1-docker.pkg.dev/$(PROJECT_ID)/app/pdf-assistant:latest

deploy:
	gcloud run deploy pdf-assistant-api \
      	--image asia-northeast1-docker.pkg.dev/$(PROJECT_ID)/app/pdf-assistant:latest \
      	--add-cloudsql-instances $(PROJECT_ID):asia-northeast1:pdf-assistant \
      	--region asia-northeast1 \
      	--cpu 1000m \
        --memory 1Gi \
        --port 8080 \
      	--platform managed \
      	--no-allow-unauthenticated \
      	--service-account cloud-run-sa@$(PROJECT_ID).iam.gserviceaccount.com \
      	--set-env-vars PROJECT_ID=$(PROJECT_ID) \
      	--ingress all \
      	--command "sh" \
      	--args "-c,python -m entrypoint.api"

	gcloud run jobs deploy clean-openai-assistant \
        --image asia-northeast1-docker.pkg.dev/$(PROJECT_ID)/app/pdf-assistant:latest \
        --set-cloudsql-instances $(PROJECT_ID):asia-northeast1:pdf-assistant \
        --region asia-northeast1 \
        --cpu 1000m \
        --memory 512Mi \
        --service-account cloud-run-sa@$(PROJECT_ID).iam.gserviceaccount.com \
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
	./cloud_sql/proxy $(PROJECT_ID):asia-northeast1:pdf-assistant