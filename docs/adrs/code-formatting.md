# Code Formatting ADR

Date: ``18-04-2024``

## Status

__ACCEPTED__

## Context

Proper code formatting is vital to the long-term viability and maintainability of a code
base. In place, a codebase with such formatting is:

- easier to review
- easier to diff against previous commits
- more likely to be free of linting errors

## Proposal

- We use [Black](https://github.com/python/black) as code formatter for the back-end codebase.
- We use Black's default options.
- We CI to ensure PRs are appropriately formatted before being accepted.
- We use [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode) as code formatter for the front-end codebase.

## Consequences
Code in the repository is pretty and uniform.


