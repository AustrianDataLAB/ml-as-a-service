# Persistence Service
``!!! This is a littlebit less dirty prototype - i guess you can take it somewaht serious !!!``

This service is used to handle userdate in a certralized way



# Endpoints
Note: All endpoints appart from ``/`` require an auth header of form ``<userid>-<token>``.
The form is due for change when the auth-token-style is fixed project wide.
## Implemented
- ``GET /``: Hello world - kinda obsolete tbh
- ``GET /healthcheck``: returns 200, ok if the service is up and running
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

# K8
## Step by step
- `` kubectl create namespace <namespace-name>`` create new namespace for the deployment so we can clean up easily
- `` kubectl apply -f azurite.yaml -n <namespace-name>`` deploy azurite first since persistence depends on it
- `` kubectl apply -f persistence.yaml -n <namespace-name>`` deploy persistence
- `` kubectl port-forward -n <namespace-name> service/persistence-service 5000:5000`` forward ports

## "Automatically"
- ``make deploy``
- ``make forward``