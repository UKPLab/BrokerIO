#!make
include .env
export

.PHONY: default
default: help

.PHONY: help
help:
	@echo "make clean             	Delete development files"
	@echo "make nlp_dev          	Run the flask app. Requires you to run make nlp_services in another terminal first"
	@echo "make build_nlp      		Build NLP services"


.PHONY: clean
clean:
	rm -r nlp/grobid_client_python

.PHONY: nlp_dev
nlp_dev:
	@echo "$(GROBID_HOST)"
	export PYTHON_PATH="$(CURDIR)/nlp/src"
	python3 ./nlp/src/app.py --dev

.PHONY: nlp_celery
nlp_celery:
	export C_FORCE_ROOT=true
	set -a
	source .env

	cd ./nlp/src && \
	celery --app app.celery worker -l INFO -E

.PHONY: build_nlp
build_nlp:
	docker-compose up grobid \
 					  rabbitmq \
 					  redis \
 					  celery-worker