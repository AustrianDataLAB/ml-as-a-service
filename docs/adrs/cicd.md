# CICD ADR

Date: ``18-04-2024``

## Status

__ACCEPTED__

## Context

We need to decide on a CI/CD solution for our project, so we can automate certain tasks, e.g., building, testing, releasing, etc..

## Decision

- Use github actions for CI

- Use github actions for CD (if possible) - az devops otherwise

- Each "finished" service needs at least a build pipeline on github

- Failing tests should block build pipelines (this can be circumvented manually in special cases if neccessary)


## Consequences

By using github for ci and cd everything is in one place which helps keeping an overview.
