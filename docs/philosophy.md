# musicaudit Philosophy

`musicaudit` exists to help protect and validate curated digital music collections.

It is not a music player.
It is not a tag editor.
It is not a library manager.
It is not intended to own the user's data.

It is an audit and quality assurance tool.

## Core Principles

### 1. Read-only by default

`musicaudit` must never modify music files, tags, playlists, XML files, artwork, lyrics, filenames, or directory structures unless the user explicitly runs a clearly write-oriented command.

Audit commands must be safe to run at any time.

If write-capable commands are ever added, they should:

- live under an obviously separate command namespace
- default to dry-run behavior
- show exactly what would change
- require explicit user confirmation or flags before writing
- never be mixed into ordinary audit commands

### 2. The music files are the source of truth

The canonical library lives in the audio files and their embedded metadata.

Apple Music, iTunes XML, playlists, databases, and sync tools are derived views of that data.

`musicaudit` should prefer facts measured from the files themselves whenever possible.

### 3. Apple Music XML is a provider, not the product

Apple Music XML is currently the first provider because it is useful and available.

It should not define the long-term architecture.

Future providers may include:

- filesystem scans
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
   |-- terminal
   |-- markdown
   |-- json
   |-- csv
   |-- yaml
```

JSON should be the primary machine-readable format.

Markdown and terminal output should be optimized for humans.

### 6. Every bug deserves a regression test

If a bug is found, the fix is not complete until there is a test that would have caught it.

Examples from early development:

- low-bitrate threshold mismatch between config and rules
- verify alias missing parser options
- over-aggressive refactor changing `set_defaults`
- empty Smart Playlists being treated as errors

These should never reappear silently.

### 7. Prefer boring, maintainable code

Avoid cleverness when plain code will do.

A rule should be easy to read, easy to test, and easy to delete.

Simple modules are better than large central files.

Small result objects are better than parsing formatted text.

Explicit configuration is better than hidden behavior.

### 8. Delete bad abstractions early

A working implementation is not necessarily a good implementation.

If the architecture is fragile, replace it before other code depends on it.

It is better to discard a bad approach early than to support it forever.

### 9. Reports should emphasize exceptions

Large curated libraries can contain tens of thousands of tracks.

Most reports should focus on things that need attention.

Detailed reports are still important, but normal output should help the user answer:

```text
Is the library healthy?
What changed?
What needs attention?
```

### 10. The tool should support long-lived collections

Digital music collections often live for decades.

`musicaudit` should be designed for long-term maintenance, not short-term convenience.

That means:

- stable CLI behavior
- clear configuration
- strong tests
- predictable output
- no hidden writes
- portable metadata assumptions
- careful versioning


## Code is read more often than it is written

Optimize for the reader.
A module should be understandable without tracing the entire program.
Small, well-defined components are preferred over large, clever implementations.
If the intent is not obvious, improve the design before adding comments.

## Build from demonstrated need

New features should be driven by repeated real-world use.

Interesting ideas are recorded.

Repeated pain points are implemented.

The existence of an idea is not sufficient reason to add it.



## Design Identity

`musicaudit` is best thought of as:

```text
fsck for digital music collections
```

or:

```text
git status / git diff for curated audio libraries
```

It should help users understand the state of their collection before syncing, backing up, migrating, or making large metadata changes.

## Non-Goals

`musicaudit` should not try to become:

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
Does this help the user validate, understand, preserve, or safely compare a curated music collection?
```

If not, it probably belongs somewhere else.

## Project Motto

```text
Trust the files.
Verify everything.
Change nothing unless explicitly told to.
```
