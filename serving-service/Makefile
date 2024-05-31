IMAGE_NAME := mlaas-service-serving
CONTAINER_NAME := serving-container

.PHONY: build up down stop test

build:
	docker build -t $(IMAGE_NAME) -f Dockerfile .

up:
	docker-compose up --build -d

down:
	docker-compose down --remove-orphans

test: 
	docker compose -f test/docker-compose-test.yaml up --build --abort-on-container-exit