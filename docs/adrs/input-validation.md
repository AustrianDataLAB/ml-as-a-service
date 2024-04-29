# User input validation ADR
Date: ``18-04-2024``

## Status

__ACCEPTED__

## Context
We need to decide on a (simple) input validation approach for our user inputs.

## Decision
- Validate input size
- Validate input structure
- Validate input file format

Validation needs to be done in:
- Persistence service

## Consquence
Only valid inputs can reach our storage.