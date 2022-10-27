#!make
include .env
export

.PHONY: default
default: help

.PHONY: help
help:
	@echo "make clean             	Delete development files"
	@echo "make dev          		Run the flask app. Requires you to run make nlp_services in another terminal first"
	@echo "make test				Run unittests"
	@echo "make build      			Build NLP services"
	@echo "make env_create			Create a virtual environment"
	@echo "make env_activate		Activate the virtual environment"
	@echo "make env_update			Update the virtual environment"

.PHONY: clean
clean:
	docker-compose rm -f -s -v
	docker network rm nlp_api_default

.PHONY: dev
dev:
	@echo "$(GROBID_HOST)"
	export PYTHONPATH="${PYTHONPATH}:$(CURDIR)" && python3 ./broker/app.py --dev

.PHONY: test
test:
	python -m unittest discover test

.PHONY: celery
celery:
	export C_FORCE_ROOT=true
	set -a
	#source .env

	#cd ./nlp/broker && \
	export PYTHONPATH="${PYTHONPATH}:$(CURDIR)" && cd ./broker && celery --app celery_app.celery worker -l INFO -E

.PHONY: build
build:
	docker-compose up rabbitmq \
 					  redis \
 					  celery-worker

.PHONY: env_create
env_create:
	conda env create -f environment.yaml

.PHONY: env_activate
env_activate:
	conda activate nlp_api

.PHONY: env_update
env_update:
	conda env update --file environment.yaml --name nlp_api --prune
