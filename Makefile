#!make
include .env
ifdef ENV
	include .env.${ENV}
endif
export

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
dev: docker
	make celery & export PYTHONPATH="${PYTHONPATH}:$(CURDIR)" && python3 ./broker/app.py --dev

.PHONY: debug
debug:
	export PYTHONPATH="${PYTHONPATH}:$(CURDIR)" && python3 ./broker/app.py --dev --debug

.PHONY: test
test:
	python -m unittest discover test

.PHONY: celery
celery:
	export PYTHONPATH="${PYTHONPATH}:$(CURDIR)" && cd ./broker && celery --app celery_app.celery worker -l INFO -E

.PHONY: broker
broker:
	export PYTHONPATH="${PYTHONPATH}:$(CURDIR)" && python3 ./broker/app.py

.PHONY: build
build:
	docker-compose -f docker-compose.yml -p "nlp_api" --env-file ".env.main" up --build -d --no-cache

.PHONY: run
run:
	export ENV=main && docker-compose -f docker-compose.yml up

.PHONY: docker
docker:
	docker-compose up -d rabbitmq \
 					  redis

.PHONY: env_create
env_create:
	conda env create -f environment.yaml

.PHONY: env_activate
env_activate:
	conda activate nlp_api

.PHONY: env_update
env_update:
	conda env update --file environment.yaml --name nlp_api --prune
