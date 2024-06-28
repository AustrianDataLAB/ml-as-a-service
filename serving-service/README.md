# Serving Service

This service is used to serve trained models to do inference.

# Endpoints
- ``GET /``: check if the service is up, returns "Hello, World!"
- ``POST /infere``: user can infer a result by sending a request with a picture

# TODO

# Quickstart
## Requirements
- Docker
- Make

## Howto
- ``make build`` to build the service image
- ``make up/down`` if to run/cleanup the service+local backend in containers
- ``make test`` to run the tests
