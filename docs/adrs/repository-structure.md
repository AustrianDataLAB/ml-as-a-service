# Repository Structure ADR

Date: ``18-04-2024``

## Status

__ACCEPTED__

## Context

We need to decide on a structre within our repository as well as a naming convention for branches and issues.

## Decision
### Repository structure
- each service has its ``own directory`` in the top level
- tests of each service are within the respective ``test`` directories
    - all files related to testing should reside in the test subdirectory

- each service has a Dockerfile in its directory

- infrastructure automation code in a toplevel ``tf`` directoy

- helmchart should reside in ``ml-as-a-service`` toplevel directory

### Branches 
We decided on the following structure:
- `main` for the main branch
- `dev` for the development branch
- `feature/` for all branches that implement a new functionality or feature
- `hotfix/` for all branches that are concerned with a bug-fix

### Issues
Issue for each feature. Optionally tickboxes for finer grained todos with the features.


## Consequences
