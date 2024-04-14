SHELL := /usr/bin/env bash

IMAGE_NAME := mlaas-service-persistence
CONTAINER_NAME := persistence-container
AUTH_TOKEN := Authorization: asoijkudhfglaskldf-101234
PORT = 1919

SEP = "----------------------------------------"

.PHONY: build up run stop test
build:
	docker build -t $(IMAGE_NAME) -f Dockerfile .
#	docker tag $(IMAGE_NAME) image

up:
	docker run -p $(PORT):5000 --name $(CONTAINER_NAME) $(IMAGE_NAME)

run:
	docker run -d -p $(PORT):5000 --name $(CONTAINER_NAME) $(IMAGE_NAME)

stop:
	docker stop $(CONTAINER_NAME)
	docker rm $(CONTAINER_NAME)

test: 
	$(eval test_file := ./test/data/corki.webp)
	$(eval tmp_dir := ./test/tmp)
	$(eval tmp_file := ./test/tmp/file)
	
	curl -X POST -H "$(AUTH_TOKEN)" -F "file=@$(test_file)" http://localhost:$(PORT)/data
	mkdir -p $(tmp_dir)
	curl -o $(tmp_file) -H "$(AUTH_TOKEN)" http://localhost:$(PORT)/data

	if diff $(tmp_file) $(test_file) > /dev/null; then \
		echo $(SEP); \
        echo "Files are the same - test successful"; \
		echo "Removing temporary files"; \
		echo $(SEP); \
		rm -rf $(tmp_dir); \
    else \
		echo $(SEP); \
        echo "Files are different"; \
		echo "Temporary files wont be removed"; \
		echo $(SEP); \
    fi
	