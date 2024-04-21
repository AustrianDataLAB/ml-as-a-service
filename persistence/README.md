# Persistence Service
``!!! This is a very dirty prototype - do not take it all too serious!!!``

This service is used to handle userdate in a certralized way



# Endpoints
All endpoints appart from ``/`` require an auth header of form ``<userid>-<token>``.
## Already implemented
- ``GET /``: Hello world - this could later be adapted to heartbeat if required
- ``POST /data``: user can store file (its meant to be a zip archive however thats not enforeced atm)
- ``GET /data``: user can fetch their data

# TODO

- ``POST /model``: post pretrained model (to be served later on)
- ``GET /model``: get trained model
- (optionally) ``Further CRUD``: deletes?
- ``logging``
- `` proper directory structure``: (depending on actual storage solution (az bucket mounted vs ....)

# Quickstart
## Requirements
- Docker
- Make
- curl

## Howto
```
make build
make run
make test
make stop
```
