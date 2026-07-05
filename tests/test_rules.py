from musicaudit.rules.engine import run_rules
from musicaudit.analysis import audit_core
from musicaudit.model import Library
from musicaudit.settings import Settings


def make_library(tracks, config=None, low_bitrate=256):
    return Library(
        xml_path="test.xml",
        tracks=tracks,
        playlists=[],
        known_tokens={"FAV"},
        config=config or {},
        settings=Settings(low_bitrate=low_bitrate),
    )


def test_missing_rating_rule_detects_unrated_track():
    lib = make_library(
        [
            {
                "name": "A",
                "artist": "X",
                "album": "Y",
                "comments": "S5",
                "bit_rate": 320,
                "path": None,
                "kind": "MPEG audio file",
            },
            {
                "name": "B",
                "artist": "X",
                "album": "Y",
                "comments": "",
                "bit_rate": 320,
                "path": None,
                "kind": "MPEG audio file",
            },
        ]
    )
    core = audit_core(lib, scan_files=False, low_bitrate=256)
    results = run_rules(lib, core, False, 256, ["missing-rating"])
    assert results[0].id == "missing-rating"
    assert results[0].count == 1


def test_low_bitrate_uses_resolved_threshold():
    lib = make_library(
        [
            {
                "name": "A",
                "artist": "X",
                "album": "Y",
                "comments": "S5",
                "bit_rate": 64,
                "path": None,
                "kind": "MPEG audio file",
            },
            {
                "name": "B",
                "artist": "X",
                "album": "Y",
                "comments": "S5",
                "bit_rate": 320,
                "path": None,
                "kind": "MPEG audio file",
            },
        ]
    )
    core = audit_core(lib, scan_files=False, low_bitrate=128)
    results = run_rules(lib, core, False, 128, ["low-bitrate"])
    assert results[0].count == 1
    assert "128" in results[0].description

    core = audit_core(lib, scan_files=False, low_bitrate=10)
    results = run_rules(lib, core, False, 10, ["low-bitrate"])
    assert results[0].count == 0
    assert "10" in results[0].description


def test_empty_smart_playlist_not_reported_as_empty_standard():
    lib = Library(
        xml_path="test.xml",
        tracks=[],
        playlists=[
            {
                "name": "Validate Missing Ratings",
                "is_smart": True,
                "folder": False,
                "item_count": 0,
            }
        ],
        known_tokens={"FAV"},
        config={},
        settings=Settings(),
    )
    core = audit_core(lib, scan_files=False, low_bitrate=256)
    results = run_rules(lib, core, False, 256, ["empty-standard-playlist"])
    assert results[0].count == 0
