IMAGE_NAME := mlaas-service-training
CONTAINER_NAME := training-container
NETWORK_NAME := persistence_test_network

.PHONY: build build-test up run stop 
build:
	docker build -t $(IMAGE_NAME) -f Dockerfile .

build-test:
	docker build -t $(IMAGE_NAME) -f Dockerfile.test .

run:
	docker run -d --network=$(NETWORK_NAME) --name $(CONTAINER_NAME) $(IMAGE_NAME)

stop:
	docker stop $(CONTAINER_NAME)
	docker rm $(CONTAINER_NAME)