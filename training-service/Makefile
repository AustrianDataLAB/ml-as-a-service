IMAGE_NAME := mlaas-service-training
CONTAINER_NAME := training-container

.PHONY: build build-test up run stop 
build:
	docker build -t $(IMAGE_NAME) -f Dockerfile .

build-test:
	docker build -t $(IMAGE_NAME) -f Dockerfile.test .

run:
	docker run -d --name $(CONTAINER_NAME) $(IMAGE_NAME)

stop:
	docker stop $(CONTAINER_NAME)
	docker rm $(CONTAINER_NAME)

up:
	docker-compose up --build -d

down:
	docker-compose down --remove-orphans