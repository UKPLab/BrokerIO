#!make
include .env  #default env
ifdef ENV
	include .env.${ENV}
endif
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
	@echo "make docker		  	    Start docker images for local development"
	@echo "make doc 			 	Generate documentation"

.PHONY: dev
dev: docker
	make celery & make run

.PHONY: doc
doc: doc_asyncapi doc_sphinx

.PHONY: clean_doc
clean_doc:
	cd ./docs && make clean
	rm -rf docs/docs

.PHONY: doc_asyncapi
doc_asyncapi:
	docker run --rm -v ${PWD}/docs/api.yml:/app/api.yml -v ${PWD}/docs/html:/app/output asyncapi/generator --force-write -o ./output api.yml @asyncapi/html-template

.PHONY: doc_sphinx
doc_sphinx:
	cd docs && make clean
	cd docs && make html

.PHONY: run
run:
	export PYTHONPATH="${PYTHONPATH}:$(CURDIR)" && python3 ./broker/app.py --dev

.PHONY: test
test:
	cd test && python -m unittest discover

.PHONY: debug
debug:
	export PYTHONPATH="${PYTHONPATH}:$(CURDIR)" && python3 ./broker/app.py --dev --debug

.PHONY: celery
celery:
	export PYTHONPATH="${PYTHONPATH}:$(CURDIR)" && cd ./broker && celery --app celery_app.celery worker -l INFO -E

.PHONY: broker
broker:
	export PYTHONPATH="${PYTHONPATH}:$(CURDIR)" && python3 ./broker/app.py

.PHONY: build
build:
	docker-compose -f docker-compose.yml -p "nlp_api_main" --env-file ".env.main" up --build -d

.PHONY: build-dev
build-dev:
	docker-compose -f docker-compose.yml -p "nlp_api_dev" --env-file ".env.dev" up --build -d

.PHONY: build-dev-clean
build-dev-clean:
	docker-compose -p "nlp_api_dev" rm -f -s -v
	docker network rm nlp_api_dev_default || echo "IGNORING ERROR"

.PHONY: build-clean
build-clean: clean
	docker-compose -p "nlp_api_main" rm -f -s -v
	docker network rm nlp_api_main_default || echo "IGNORING ERROR"

.PHONY: clean
clean:
	docker-compose rm -f -s -v
	docker network rm nlp_api_default || echo "IGNORING ERROR"

.PHONY: docker
docker:
	docker-compose -f docker-dev.yml up rabbitmq redis

.PHONY: env_create
env_create:
	conda env create -f environment.yaml

.PHONY: env_activate
env_activate:
	conda activate nlp_api

.PHONY: env_update
env_update:
	conda env update --file environment.yaml --name nlp_api --prune
