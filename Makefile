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
	@echo "make docker      		Build all docker images - complete environment"
	@echo "make build 		   	    Build the python package"
	@echo "make build-wheel			Build the python package as a wheel"
	@echo "make build-sdist			Build the python package as a source distribution"
	@echo "make db			    	Start docker containers for db"
	@echo "make check				Run a twine check on the package"
	@echo "make upload				Upload the package to pypi"
	@echo "make key	            	Generate private key"
	@echo "make test				Run tests"
	@echo "make stress            	Run stress test"
	@echo "make doc 			 	Generate documentation"
	@echo "make env_create			Create a virtual environment"
	@echo "make env_update			Update the virtual environment"

.PHONY:key
key:
	openssl genrsa -out private_key.pem 2048

.PHONY: build
build:
	python3 -m build

.PHONY: build-sdist
build-sdist:
	python3 -m build --sdist

.PHONY: build-wheel
build-wheel:
	python3 -m build --wheel

.PHONY: check
check:
	twine check dist/*

.PHONY: upload
upload:
	twine upload dist/*

.PHONY: clean
clean:
	rm -f private_key.pem
	rm -rf BrokerIO.egg-info
	rm -rf build
	docker compose rm -f -s -v
	docker network rm brokerio_default || echo "IGNORING ERROR"

.PHONY: docker
docker:
	docker compose -f docker-compose.yml -p "brokerio" up --build -d

.PHONY: docker-dev
docker-dev:
	docker compose --env-file .env.dev -f docker-compose.yml -p "brokerio_dev" up --build -d

.PHONY: db
db:
	docker compose -f docker-compose.yml -f docker-dev.yml up arangodb redis

.PHONY: test
test:
	export PYTHONPATH="${PYTHONPATH}:${CURDIR}" && python3 -u -m unittest test.test_broker.TestBroker

.PHONY: test_all
test_all:
	export PYTHONPATH="${PYTHONPATH}:${CURDIR}" && python3 -m unittest discover test

.PHONY: stress
stress:
	export PYTHONPATH="${PYTHONPATH}:${CURDIR}" && python3 -u -m unittest test.test_broker.TestBroker.stressTest

.PHONY: test-cli
test-cli:
	export PYTHONPATH="${PYTHONPATH}:${CURDIR}" && python3 -u -m unittest test.test_cli.TestCLI

.PHONY: test-build
test-build:
	docker exec --env-file .env.main brokerio-broker-1 python3 -u -m unittest test.test_broker.TestBroker

.PHONY: test-build-dev
test-build-dev:
	docker exec --env-file .env.dev brokerio_dev-broker-1 python3 -u -m unittest test.test_broker.TestBroker

.PHONY: test-stress
test-stress:
	docker exec --env-file .env.main brokerio-broker-1 python3 -u -m unittest test.test_broker.TestBroker.stressTest
	docker cp brokerio-broker-1:/tmp/stress_results.csv ./test/stress_results.csv

.PHONY: test-stress-dev
test-stress-dev:
	docker exec --env-file .env.dev brokerio_dev-broker-1 python3 -u -m unittest test.test_broker.TestBroker.stressTest
	docker cp brokerio_dev-broker-1:/tmp/stress_results.csv ./test/stress_results.csv

.PHONY: build-dev-clean
build-dev-clean:
	docker compose -p "brokerio_dev" rm -f -s -v
	docker network rm brokerio_dev_default || echo "IGNORING ERROR"

.PHONY: build-clean
build-clean: clean
	docker compose -p "brokerio" rm -f -s -v
	docker network rm brokerio_default || echo "IGNORING ERROR"

.PHONY: env_create
env_create:
	conda env create -f environment.yaml

.PHONY: env_update
env_update:
	conda env update --file environment.yaml --name brokerio --prune

.PHONY: doc
doc: doc_asyncapi doc_sphinx

.PHONY: clean_doc
clean_doc:
	cd ./docs && make clean
ifeq ($(OS),Windows_NT)
	rmdir /S /Q docs\docs
else
	rm -rf docs/docs
endif

.PHONY: doc_asyncapi
doc_asyncapi:
	docker run --rm -v ${CURDIR}/docs/api.yml:/app/api.yml -v ${CURDIR}/docs/html:/app/output asyncapi/generator:1.15.5 --force-write -o ./output api.yml @asyncapi/html-template

.PHONY: doc_sphinx
doc_sphinx:
	docker compose -f docker-compose.yml build docs_sphinx
	docker run --rm -v ${CURDIR}/docs:/docs broker_docs_sphinx make html


