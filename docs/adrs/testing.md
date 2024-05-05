# Testing ADR

Date: ``18-04-2024``

## Status

__ACCEPTED__

## Context

We need to decide on a testing solution for our project.

## Decision

- Blocking tests in the respective build pipelines

- Each service should have tests ensuring its (core) functionallity (unit testing)

- Tests should be done in a containerized way with dockercompse (as shown in the lectures) can be omitted if not feasable (i.e k8 operator)


## Consequences

Images with failing tests cannot be automatically pushed to the registry.