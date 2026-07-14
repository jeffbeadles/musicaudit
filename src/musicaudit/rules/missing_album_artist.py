from .base import Rule, RuleResult, register_rule


@register_rule
class MissingAlbumArtistRule(Rule):
    id = "missing-album-artist"
    level = "WARN"
    description = "Albums with multiple artists but no Album Artist"
    long_description = "Albums with multiple artists, missing album_artist tag"

    def run(self, library, core):
        problems = []
        albums = {}
        for track in library.tracks:
            album = (track.get("album") or "").strip()
            if not album:
                continue
            albums.setdefault(album.lower(), []).append(track)

        for tracks in albums.values():
            artists = {t.get("artist", "") for t in tracks if t.get("artist")}
            album_artists = {
                t.get("album_artist", "") for t in tracks if t.get("album_artist")
            }
            if len(artists) > 1 and not album_artists:
                problems.append(tracks[0])

        return RuleResult(self.id, self.level, self.description, problems)
