SHELL := /usr/bin/env bash

IMAGE_NAME := mlaas-service-persistence
CONTAINER_NAME := persistence-container

NAMESPACE := deployment-test

SEP = "----------------------------------------"

.PHONY: build up down azurite test deploy cleanup debug
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


deploy:
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -
	kubectl apply -f k8s/azurite.yaml -n $(NAMESPACE)
	kubectl apply -f k8s/persistence.yaml -n $(NAMESPACE)

forward:
	kubectl port-forward -n $(NAMESPACE) service/persistence-service 5000:5000

cleanup:
	kubectl delete namespace $(NAMESPACE)