# Storage Solution ADR

Date: ``18-04-2024``

## Status

__ACCEPTED__

## Context

We need to decide on a storage solution for our project.

## Decision

KISS: use a single azure blob storage (pivot to nfs if blob storage doesnt work out for some reason)

Within the bucket: directory for each user (hash of userid) with subdirectories for data and model:
```
bucket
|
+-- <hash(user-id)>
   |
   +-- data
   |
   +-- model
```
Accessed only from persistence-service via azure sdk.


## Consequences
Loose coupleing. Storage solution can easily be swapped out since storage details are abstracted away by the persistence service.