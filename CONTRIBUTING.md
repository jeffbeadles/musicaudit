# Contributing to musicaudit

Thank you for your interest in contributing.

Before proposing a new feature, please consider whether it aligns with the
project's goals.

## Project Goals

musicaudit is a read-only validation engine for digital music collections.

The goal is to accurately describe the health of a collection and provide
stable human-readable and machine-readable output.

## Project Contracts

The following contracts are considered fundamental to the project.

### Read-only

musicaudit does not modify music files or music libraries.

There will never be a general-purpose "fix" or "write" mode.

### Stable JSON

The JSON output is a public interface.

Existing fields are never removed or redefined.

New fields may be added.

### Validation First

Rules should identify problems completely.

They should provide enough information for another tool to locate and resolve
the issue.

### Small Scope

musicaudit performs validation.

It intentionally does not perform metadata editing, artwork downloading,
renaming, or other maintenance tasks.

Those are encouraged as separate tools.
