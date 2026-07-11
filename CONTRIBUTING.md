# Contributing to musicaudit

Thank you for your interest in contributing.

Before proposing a new feature, please consider whether it aligns with the
project's goals and direction.

## Project Goals

musicaudit is a read-only validation engine for digital music collections.

The goal is to accurately describe the health of a collection and provide
stable human-readable and machine-readable output.

## Project Contracts

See CONTRACTS.md

### Validation First

Rules should identify problems completely.

They should provide enough information for another tool to locate and resolve
the issue.

### Small Scope

musicaudit performs validation.

It is not a music player.
It is not a tag editor.
It is not a library manager.
It does not own the user's data.

It intentionally does not perform metadata editing, artwork downloading,
renaming, or other maintenance tasks.

Those are encouraged as separate tools.

### Coding standards, requirements, and norms

Once the git repository is cloned, it is recommended that the hooks directory is
properly configured.  If not, your commit may fail when pushed to github.
git config core.hooksPath `pwd`/tools/hooks

Read docs/philosophy.md before making any changes.

See requirements-dev.txt for packages required for development.

Before any push request, a regression test must be added for any new or changed functionality.

Also, the command ./tools/hooks/pre-push must be run and pass without warnings or errors before pushing to github.  This checks formatting, code, and regression tests.

Note, that these are also run as part of github's CI flow, and are not optional.

User-contributed scripts may be placed in contrib/ . They must contain information
on what they do, how to use them, and who to contact with questions or issues.

