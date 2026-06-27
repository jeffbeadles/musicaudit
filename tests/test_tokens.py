from musicaudit.model import analyze_comment_tokens


def test_valid_rating_and_fav():
    info = analyze_comment_tokens("FAV S5", {"FAV"})
    assert info["rating"] == "S5"
    assert info["favorite"] is True
    assert info["unknown_tokens"] == []


def test_missing_rating():
    info = analyze_comment_tokens("FAV", {"FAV"})
    assert info["rating"] is None
    assert info["missing_rating"] is True


def test_multiple_ratings():
    info = analyze_comment_tokens("S4 S5", {"FAV"})
    assert info["multiple_ratings"] is True


def test_bad_rating():
    info = analyze_comment_tokens("S9", {"FAV"})
    assert info["bad_ratings"] == ["S9"]


def test_unknown_token():
    info = analyze_comment_tokens("S5 LIVE", {"FAV"})
    assert info["unknown_tokens"] == ["LIVE"]
