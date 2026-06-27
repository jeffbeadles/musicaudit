# musicaudit Roadmap and Project Plan

## Current Status

The prototype has proven the concept and the architecture is taking
shape.

-   Core concept validated
-   Modular rule engine
-   Central settings resolver
-   Initial unit and integration tests
-   Project philosophy documented
-   Git repository established
-   Dedicated Python virtual environment created

**Target:** Stabilize before Version 1.0.

------------------------------------------------------------------------

# Phase 1 -- Stabilization

## Architecture

Complete the separation of responsibilities:

``` text
CLI
  ↓
Settings
  ↓
Provider
  ↓
Analysis
  ↓
Rules
  ↓
Result Model
  ↓
Renderer
```

Goals:

-   Finish provider abstraction
-   Finish renderer abstraction
-   Keep commands as orchestration only
-   Continue reducing module coupling

## Testing

Expand automated testing.

### XML fixtures

-   Clean library
-   Missing ratings
-   Duplicate tracks
-   Compilation albums
-   Missing files
-   Invalid XML
-   Empty library
-   Nested playlists
-   Duplicate persistent IDs

### Audio fixtures

Include MP3, M4A, ALAC and FLAC with known metadata to verify:

-   Embedded artwork
-   Embedded lyrics
-   Bitrate
-   Embedded tags
-   Corrupt files

### Regression tests

Every bug fixed becomes a permanent regression test.

Examples already captured:

-   Low bitrate configuration
-   Verify alias parser
-   CLI parser refactoring

## Packaging

-   pyproject.toml
-   requirements-dev.txt
-   LICENSE
-   README
-   Documentation
-   Tests

Goal:

``` bash
pip install musicaudit
```

## Documentation

Create:

-   installation.md
-   quickstart.md
-   configuration.md
-   rules.md
-   architecture.md
-   development.md
-   contributing.md

------------------------------------------------------------------------

# Phase 2 -- Version 1.0

Freeze the public interface.

Stable:

-   CLI
-   Configuration
-   Plugin API
-   Report formats
-   Test suite

------------------------------------------------------------------------

# Phase 3 -- Rule Engine

Continue expanding modular rules.

Each rule should have:

-   One module
-   One test file
-   One documentation section

Potential rules include:

-   Missing ratings
-   Duplicate tracks
-   Missing album artist
-   Missing lyrics
-   Missing artwork
-   XML tag mismatch
-   Duplicate persistent IDs
-   Invalid filenames
-   Missing year
-   Missing genre

------------------------------------------------------------------------

# Phase 4 -- Providers

Apple Music becomes only one provider.

Future providers:

-   Filesystem
-   beets
-   MusicBrainz / Picard
-   foobar2000

Rules should never depend on the provider.

------------------------------------------------------------------------

# Phase 5 -- Renderers (Version 2)

Introduce a renderer layer.

``` text
Analysis
    ↓
Result Objects
    ↓
Renderers
      • Terminal
      • Markdown
      • JSON
      • CSV
      • YAML
```

JSON should be the canonical machine-readable format.

------------------------------------------------------------------------

# Future Ideas

-   `doctor` command
-   Historical snapshots
-   Backup verification
-   Timeline reports
-   Machine-readable automation output

------------------------------------------------------------------------

# Non-goals

musicaudit is **not** intended to become:

-   Music player
-   Tag editor
-   Ripper
-   Streaming client
-   Artwork downloader
-   Lyrics downloader
-   Media manager

------------------------------------------------------------------------

# Living Project Documents

Maintain these in the repository:

``` text
ROADMAP.md
TODO.md
docs/philosophy.md
docs/architecture.md
```

Purpose:

-   ROADMAP: strategic direction
-   TODO: tactical work
-   Philosophy: design principles
-   Architecture: how the pieces fit together

------------------------------------------------------------------------

# Project Philosophy

-   Trust the files.
-   Verify everything.
-   Change nothing unless explicitly told to.
-   Every bug becomes a regression test.
-   Prefer deleting weak abstractions over maintaining them forever.

------------------------------------------------------------------------

# Immediate Recommendation

Use `musicaudit` as part of the normal workflow.

Whenever a bug is found:

1.  Write a failing test.
2.  Fix the bug.
3.  Commit both together.

Let real-world use drive future development rather than hypothetical
features.
