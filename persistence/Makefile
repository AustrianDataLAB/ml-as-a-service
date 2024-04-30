SHELL := /usr/bin/env bash

IMAGE_NAME := mlaas-service-persistence
CONTAINER_NAME := persistence-container

SEP = "----------------------------------------"

.PHONY: build up run stop down azurite test
build:
	docker build -t $(IMAGE_NAME) -f Dockerfile .
	docker build  -t $(IMAGE_NAME)-tester -f Dockerfile.test .

up:
	docker-compose up --build -d

down:
	docker-compose down --remove-orphans

azurite:
	docker-compose -f docker-compose.yaml  run --build azurite

test: 
	docker compose -f docker-compose-test.yaml up --build --abort-on-container-exit