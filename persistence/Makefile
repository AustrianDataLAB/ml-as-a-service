SHELL := /usr/bin/env bash

IMAGE_NAME := mlaas-service-persistence
CONTAINER_NAME := persistence-container
AUTH_TOKEN := Authorization: asoijkudhfglaskldf-101234
PORT = 1919

SEP = "----------------------------------------"

.PHONY: build up run stop down azurite test
build:
	docker build -t $(IMAGE_NAME) -f Dockerfile .
	docker build -f test/Dockerfile.test -t persistence-tester ./test
#	docker tag $(IMAGE_NAME) image

run:
	docker run -p $(PORT):5000 --name $(CONTAINER_NAME) $(IMAGE_NAME)

up:
#	docker run -d -p $(PORT):5000 --name $(CONTAINER_NAME) $(IMAGE_NAME)
	docker-compose up --build

stop:
	docker stop $(CONTAINER_NAME)
	docker rm $(CONTAINER_NAME)

down:
	docker-compose down --remove-orphans

azurite:
	docker-compose -f docker-compose.yaml  run --build azurite

test: 
	docker compose -f docker-compose-test.yaml up --build --abort-on-container-exit