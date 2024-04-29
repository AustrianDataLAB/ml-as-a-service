# Serving Service
``!!! Very dirty prototype only to be used for mocking the behaviour of the service !!!``
This service is meant to serve the models trained by the training service.

# Endpoints
- ``POST v1/models/half-plus-two:predict`` post instances and recieve inference as return

# TODO
basically everything

# Quickstart
## Requirements
- Docker
- Make
- curl

## Howto
- ``make build`` to build the service image
- ``make up/down`` if to run/cleanup the service in a container
- ``make test`` to run the tests locally (i.e. curl post to the service and see if it returns inference)