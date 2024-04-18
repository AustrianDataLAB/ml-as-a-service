IMAGE_NAME := mlaas-service-training
CONTAINER_NAME := training-container

.PHONY: build up run stop test
build:
	docker build -t $(IMAGE_NAME) -f Dockerfile .

up:
	docker run --name $(CONTAINER_NAME) $(IMAGE_NAME)

run:
	docker run -d --name $(CONTAINER_NAME) $(IMAGE_NAME)

stop:
	docker stop $(CONTAINER_NAME)
	docker rm $(CONTAINER_NAME)