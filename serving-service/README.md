# Serving Service

This service is used to serve trained models to do inference.

# Endpoints
- ``POST /infere``: user can store data (its meant to be a zip    achieve however thats not enforeced atm)

# TODO
- ``logic``
- ``testing``
- ``logging / exception handling``

# Quickstart
## Requirements
- Docker
- Make

## Howto
- ``make build`` to build the service image
- ``make up/down`` if to run/cleanup the service+local backend in containers
