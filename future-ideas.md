
## Rule Profiles

Status:
Deferred until after Version 1.0

Motivation:

A single global low bitrate threshold is too restrictive for mixed
collections containing music, audiobooks, podcasts, or spoken word.

Current workaround:

Lower the threshold globally.

Problems:

This weakens validation for music.

Potential solution:

Allow rules to define multiple configurable profiles.

Example:

rules:
  low-bitrate:
    profiles:
      - match:
          media_kind: music
        minimum: 256

      - match:
          genre:
            - Audiobook
        minimum: 64

Discussion:

Avoid hardcoded knowledge of audiobooks.
Generalize into a reusable policy/profile mechanism.
