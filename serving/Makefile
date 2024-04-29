SHELL := /usr/bin/env bash

IMAGE_NAME := mlaas-service-serving
CONTAINER_NAME := serving-container



SEP = "----------------------------------------"

.PHONY: build up run stop down azurite test
build:
	docker build -t $(IMAGE_NAME) -f Dockerfile .

up:
#	docker run -d -p $(PORT):5000 --name $(CONTAINER_NAME) $(IMAGE_NAME)
	docker compose up -d --build

down:
	docker compose down

test:
	curl -d '{"instances": [1.0, 2.0, 5.0]}'     -X POST http://localhost:8501/v1/models/half-plus-two:predict