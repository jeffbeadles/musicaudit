# musicaudit - Version 8.9

`musicaudit` is a read-only QA toolkit for curated digital music collections.

Version 7 adds automatic rule discovery.

Each rule now lives in its own module under `musicaudit/rules/`.
Rules self-register with the rule engine using `@register_rule`.

## Safety rule

`musicaudit` is read-only.

It does not modify music files, tags, XML files, playlists, ratings, lyrics, artwork, or file locations.

Future write-capable features, if ever added, should require explicit write-oriented commands and confirmation. The default mode of this project is audit, validate, compare, and report.

## Install optional dependencies

For embedded lyrics/artwork scanning:

```bash
python3 -m pip install mutagen
```

For Smart Playlist decoding experiments:

```bash
python3 -m pip install itunessmart
```

For config file support:

```bash
python3 -m pip install pyyaml
```

## Run from the package directory

Unzip the archive, then run:

```bash
python3 -m musicaudit health --apple-library ~/Music/Library.xml
python3 -m musicaudit summary --apple-library ~/Music/Library.xml --scan-files
python3 -m musicaudit rules --apple-library ~/Music/Library.xml --scan-files
python3 -m musicaudit diff --old before.xml --new after.xml
```

## Commands

```bash
python3 -m musicaudit health --apple-library ~/Music/Library.xml
python3 -m musicaudit summary --apple-library ~/Music/Library.xml --scan-files
python3 -m musicaudit tokens --apple-library ~/Music/Library.xml
python3 -m musicaudit playlists --apple-library ~/Music/Library.xml
python3 -m musicaudit stats --apple-library ~/Music/Library.xml
python3 -m musicaudit rules --apple-library ~/Music/Library.xml --scan-files
python3 -m musicaudit verify --apple-library ~/Music/Library.xml --scan-files
python3 -m musicaudit diff --old before.xml --new after.xml
```

`verify` is now a compatibility alias for `rules`.

## Terse output

```bash
python3 -m musicaudit health --apple-library ~/Music/Library.xml --terse
python3 -m musicaudit rules --apple-library ~/Music/Library.xml --scan-files --terse
python3 -m musicaudit diff --old before.xml --new after.xml --terse
```

## Rule engine

Discovered built-in rules currently include:

- `missing-files`
- `missing-rating`
- `invalid-rating`
- `duplicate-track`
- `low-bitrate`
- `empty-standard-playlist`
- `unknown-token`
- `missing-lyrics` with `--scan-files`
- `missing-artwork` with `--scan-files`
- `unreadable-file` with `--scan-files`
- `xml-tag-mismatch` with `--scan-files`
- `missing-album-artist`

Empty Smart Playlists are not errors. They are often validation checks where zero matching tracks means success.

Run selected rules only:

```bash
python3 -m musicaudit rules --apple-library ~/Music/Library.xml --rule missing-rating
python3 -m musicaudit rules --apple-library ~/Music/Library.xml --rule missing-rating --rule unknown-token
```

Use `--strict` for scripting:

```bash
python3 -m musicaudit rules --apple-library ~/Music/Library.xml --scan-files --strict
```

By default, ERROR rules fail and WARN rules report but do not fail. Use this to make warnings fail too:

```bash
python3 -m musicaudit rules --apple-library ~/Music/Library.xml --scan-files --fail-warnings --strict
```

## Config file

Optional config locations:

```text
~/.config/musicaudit/config.yaml
~/.musicaudit.yaml
```

Example:

```yaml
apple_library: ~/Music/Library.xml
low_bitrate: 256
bitrate_report: summary
max_details: 25
known_tokens:
  - LIVE
  - LYRICS
enabled_rules:
  - missing-files
  - missing-rating
  - invalid-rating
  - unknown-token
```

Then you can run:

```bash
python3 -m musicaudit health
python3 -m musicaudit rules --scan-files
python3 -m musicaudit stats
```

## Package layout

```text
musicaudit/
    cli.py
    model.py
    analysis.py

    commands/
        health.py
        summary.py
        tokens.py
        playlists.py
        stats.py
        rules.py
        verify.py
        diff.py

    providers/
        applemusic.py
        audio.py

    rules/
        base.py
        builtin.py

    reports/
        markdown.py

    util/
        config.py
        formatting.py
```

This should make future development much easier than editing one large script.


## Adding a new rule

Create a new file in `musicaudit/rules/`, for example:

```python
from .base import Rule, RuleResult, register_rule


@register_rule
class MyRule(Rule):
    id = "my-rule"
    level = "WARN"
    description = "Describe what this rule checks"

    def run(self, library, core):
        problems = []
        return RuleResult(self.id, self.level, self.description, problems)
```

The rule engine automatically imports rule modules and registers the rule.

## Per-rule configuration

Example:

```yaml
rules:
  duplicate-track:
    level: warning

  missing-lyrics:
    enabled: true
    level: warn

  low-bitrate:
    enabled: true
    minimum: 256

  missing-album-artist:
    enabled: true
```

You can also restrict which rules run:

```yaml
enabled_rules:
  - missing-files
  - missing-rating
  - invalid-rating
  - unknown-token
  - missing-album-artist
```


## Version 7.1 fix

Fixed low-bitrate rule configuration so the displayed threshold and warning count use the same resolved value.

Resolution order:

1. `--low-bitrate` command-line option
2. `rules.low-bitrate.threshold` or `rules.low-bitrate.minimum`
3. global `low_bitrate`
4. default `256`

Examples:

```yaml
low_bitrate: 128
```

or rule-specific:

```yaml
rules:
  low-bitrate:
    threshold: 128
```

Both the count and the rule description should now match.


## Version 7.2 fix

Fixed low-bitrate config resolution in the `rules` / `verify` path.

The rule engine now receives the source of the threshold value:

- CLI
- config
- default

This lets it apply the intended precedence correctly.

Debug the resolved config with:

```bash
python3 -m musicaudit rules --apple-library ~/Music/Library.xml --show-config
```

Expected examples:

```text
low_bitrate=10
low_bitrate_source=config
config_low_bitrate=10
```

or with CLI override:

```text
low_bitrate=128
low_bitrate_source=cli
config_low_bitrate=10
```


## Version 7.3 fix

Fixed low-bitrate rule counts when the threshold is configured under:

```yaml
rules:
  low-bitrate:
    enabled: true
    minimum: 12
```

The earlier fix corrected the displayed rule threshold, but `audit_core()` was still building
the low-bitrate track list using the default threshold. Version 7.3 resolves the effective
threshold before scanning the library so the count and label match.

Check with:

```bash
python3 -m musicaudit rules --apple-library ~/Music/Library.xml --show-config
```

Look for:

```text
effective_low_bitrate=12
effective_low_bitrate_source=rule
```


## Version 8

Version 8 introduces a centralized settings resolver and initial unit tests.

The important design change is that effective settings are resolved once in
`musicaudit/settings.py`, then passed downstream. This prevents different parts
of the program from independently deciding things like the low-bitrate threshold.

## Running tests

Install pytest:

```bash
python3 -m pip install pytest
```

From the extracted project directory:

```bash
python3 -m pytest
```

Included tests cover:

- low-bitrate precedence
- comment token parsing
- missing rating rule
- low-bitrate rule/count consistency
- empty Smart Playlists not being treated as errors


## Version 8.1

Fixed the first test failures by making `audit_core()` tolerate minimal synthetic
track dictionaries. This makes the unit tests easier to write and reduces hidden
assumptions about provider output.


## Version 8.2

Fixed a refactoring bug where `set_defaults()` was accidentally changed to
`set_apply_settings()` in command parser setup.

Added CLI integration tests for:

- `python3 -m musicaudit --help`
- each subcommand's `--help`
- `python3 -m musicaudit --version`

These tests catch parser-level failures that direct unit tests miss.


## Version 8.3

Fixed `verify`, which is a compatibility alias for `rules`, failing with:

```text
AttributeError: 'Namespace' object has no attribute 'show_config'
```

The `rules` command now uses `getattr(args, "show_config", False)`, and the
`verify` parser also exposes `--show-config`.


## Version 8.4

Added a small Apple Music XML fixture library and integration tests that exercise
the CLI through `musicaudit.cli.main()`.

New tests cover:

- health counts from fixture XML
- rules output from fixture XML
- terse rules output
- low-bitrate rule config from temporary YAML config
- diff detecting a newly added favorite
- verify alias behavior

Developer setup:

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest
```

Run only integration tests:

```bash
python3 -m pytest tests/test_integration_reports.py -v
```

A helper script is also included:

```bash
./run_tests.sh
```


## Version 8.5

Fixed user-facing error handling when the XML input file does not exist.

Previously, commands could show a Python traceback after reporting:

```text
XML file not found
```

Now the CLI catches user-facing `RuntimeError` exceptions and prints only:

```text
ERROR: XML file not found: /path/to/file.xml
```

Added regression tests to ensure missing XML input does not produce a traceback.


## Version 8.6

Fixed `unknown-token` handling so tokens listed in the rule-specific
configuration are treated as allowed tokens.

Example:

```yaml
rules:
  unknown-token:
    allowed:
      - LIVE
      - DEMO
      - REMASTER
```

These are now included in the effective known-token set used by analysis and
will not be reported as unknown comment tokens.

Added regression tests for this behavior.


## Version 8.7

Added valid JSON output for `rules` and `verify`:

```bash
python3 -m musicaudit rules --apple-library Library.xml --rule missing-album-artist --format json
python3 -m musicaudit verify --apple-library Library.xml --format json
```

The JSON renderer emits only JSON to stdout and no Markdown or human-readable
header text. This makes it suitable for scripts and for tests that parse output
with `json.loads()`.

Added regression tests for `missing-album-artist` JSON output.


## Version 8.8

Added a filesystem provider.

This allows tests and future reference libraries to be built directly from audio
files instead of relying on Apple Music XML.

Example:

```bash
python3 -m musicaudit rules --provider filesystem --path tests/reference-library/audio
python3 -m musicaudit health --provider filesystem --path /path/to/music
python3 -m musicaudit rules --provider filesystem --path /path/to/music --format json
```

The filesystem provider uses `mutagen` to read tags directly from audio files.

This is intended to become the foundation for the long-term test reference
library. Apple Music XML remains important, but primarily as an Apple Music
compatibility provider.

A helper script has been added:

```bash
scripts/generate_reference_library.sh
```

It uses `ffmpeg` to generate small redistributable dummy MP3 files for tests.


Note: the filesystem provider handles common ffmpeg-generated MP3 comment
metadata, including `TXXX:comment`, so generated reference files can be used
for comment-token tests.


## Version 8.9

Renamed the Apple Music XML input option:

```bash
--xml
```

has been removed and replaced with:

```bash
--apple-library
```

Examples:

```bash
python3 -m musicaudit rules --apple-library Library.xml
python3 -m musicaudit health --apple-library Library.xml
```

Filesystem input is now inferred from `--path`, so this works without explicitly
specifying `--provider filesystem`:

```bash
python3 -m musicaudit rules --path /path/to/music
```

The older `library_xml` config key is still accepted as a compatibility fallback,
but new configs should use:

```yaml
apple_library: ~/Music/Library.xml
```

Added regression tests for:

- `--xml` being removed
- `--apple-library` missing-file error handling
- `--path` implying the filesystem provider
