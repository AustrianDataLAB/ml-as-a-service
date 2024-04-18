# User Authentication ADR

Date: ``18-04-2024``

## Status

__ACCEPTED__

## Context

We need to decide on a (simple) authorization solution for our project, so we can authorize users.

## Decision
- Make use of ingress (nginx) capabilities for [OAUTH](https://kubernetes.github.io/ingress-nginx/examples/auth/oauth-external-auth/) (github) 
- Auth headers need to be forwarded for all endpoints since it's used for user identification by all services.

## Consequences
Only github registered users can access our application. Keeping it simple (since this project as meant as a proof of concept)