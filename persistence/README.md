# Persistence Service
``!!! This is a littlebit less dirty prototype - i guess you can take it somewaht serious !!!``

This service is used to handle userdate in a certralized way



# Endpoints
Note: All endpoints appart from ``/`` require an auth header of form ``<userid>-<token>``.
The form is due for change when the auth-token-style is fixed project wide.
## Implemented
- ``GET /``: Hello world - this could later be adapted to heartbeat if required
- ``POST /data``: user can store data (its meant to be a zip    achieve however thats not enforeced atm)
- ``GET /data``: user can fetch their data
- ``POST /model``: services/user can store models this way
- ``GET /model``: services/user can fetch their model

# TODO
- (optionally) ``Further CRUD``: deletes?
- ``logging / exception handling`` both are pretty dirty atm

# Quickstart
## Requirements
- Docker
- Make
- curl

## Howto
- ``make build`` to build the service image
- ``make up/down`` if to run/cleanup the service+local backend in containers
- ``make up`` to run the service+local backend in containers
- `` make azurite`` to run the azurite container locally
- `` make test`` to run the tests locally (this also spins up an azurite instance since its required for the tests)
