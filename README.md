# musicaudit

`musicaudit` exists to help protect and validate curated digital music collections.

musicaudit is a read-only validation engine for digital music collections.

Its purpose is to determine the health of a music collection and report its findings completely and accurately.

It intentionally does not modify collections. Instead, it provides stable human-readable and machine-readable output that can be consumed by other software.

It reduces the cost and complexity of maintaining a high-quality music collection.

A collection should be easy to validate at any time. By making problems inexpensive to find, users can focus their effort on correcting them rather than discovering them.

It deliberately separates diagnosis from treatment.

It is not a music player.
It is not a tag editor.
It is not a library manager.
It is not intended to own the user's data.

It is an audit and quality assurance tool.

It  reports facts, not preferences.

## Project Contracts

Several aspects of musicaudit are considered contractual rather than
implementation details.

### Read-only Contract

musicaudit will never modify music collections.

Users should be able to execute any musicaudit command with complete confidence
that their collection will remain unchanged.

### JSON Compatibility Contract

The JSON output is intended to be consumed by other software.

Existing field meanings and rule identifiers will remain stable.

Future releases may add new fields, but existing consumers should continue to
function without modification.

## Core Principles

### 1. Read-only, period.

`musicaudit` must never modify music files, tags, playlists, XML files, artwork, lyrics, filenames, or directory structures.  It only requires read access to the music collection.

Audit commands must be safe to run at any time.

### 2. The music files are the source of truth

The canonical library lives in the audio files and their embedded metadata.

Apple Music, iTunes XML, playlists, databases, and sync tools are derived views of that data.

`musicaudit` should prefer facts measured from the files themselves whenever possible.

### 3. There are two providers, Apple Music (--apple-library) and the filesystem (--path) . Both are simply providers, used read-only for information.


Future providers may include:

- beets databases
- MusicBrainz/Picard metadata
- other music library exports

The rule engine should not care where the library model came from.

### 4. Rules validate; they do not repair

Rules answer questions such as:

- Is every track rated?
- Are there missing files?
- Are there unknown comment tokens?
- Are duplicate tracks present?
- Are lyrics embedded?
- Is artwork embedded?
- Do embedded tags agree with the exported library?

Rules should report problems clearly.

They should not fix them.

### 5. Human-readable and machine-readable output should come from the same result model

Reports should not be hand-built separately for each output format.

The preferred long-term design is:

```text
Analysis
   |
Result objects
   |
Renderers
   |-- terminal/markdown
   |-- json
```

JSON is the primary machine-readable format.

Terminal output should be optimized for humans.

### 6. Every bug deserves a regression test

If a bug is found, the fix is not complete until there is a test that would have caught it.

Every bug found in early development had a test created for it, including

- low-bitrate threshold mismatch between config and rules
- verify alias missing parser options
- over-aggressive refactor changing `set_defaults`
- empty Smart Playlists being treated as errors
- And many more

These should never reappear silently.

### 7. Prefer boring, maintainable code

Avoid cleverness when plain code will do.

A rule should be easy to read, easy to test, optional to use, and easy to delete.

Simple modules are better than large central files.

Parse JSON, not terminal/markdown output.

Explicit configuration is better than hidden behavior.

### 8. Reports should emphasize exceptions

Large curated libraries can easily contain tens of thousands of tracks.

Most reports should focus on things that need attention.

Detailed reports are still important, but normal output should help the user answer:

```text
Is the library healthy?
What changed?
What needs attention?
```

### 9. The tool should support long-lived collections

Digital music collections often live for decades.

`musicaudit` is designed for long-term maintenance, not short-term convenience.

This means:

- stable CLI behavior
- clear configuration
- strong tests
- predictable output
- no writes, ever
- portable metadata assumptions
- careful versioning


## Code is read more often than it is written

Optimize for the reader.
A module should be understandable without tracing the entire program.
Small, well-defined components are preferred over large, clever implementations.
If the intent is not obvious, improve the design before adding comments.

## Design Identity

`musicaudit` is best thought of as:

```text
fsck -n for digital music collections
```

or:

```text
git status / git diff for curated audio libraries
```

It should help users understand the state of their collection before syncing, backing up, migrating, or making large metadata changes.

## Non-Goals

`musicaudit` will not try to become:

- a music player
- a streaming client
- a tag editor
- an album art downloader
- a lyrics downloader
- a ripper
- a recommendation engine
- a general media manager

Those tools already exist.

`musicaudit` should integrate with them by validating the resulting collection.

## Guiding Question

Before adding a feature, ask:

```text
Does this help the user validate, understand, preserve, or safely compare their music collection?
```

If not, it probably belongs somewhere else.

## Project Motto

```text
Trust the files.
Verify everything.
Change nothing.
```
