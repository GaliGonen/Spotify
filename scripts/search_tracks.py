import os
import json
import argparse
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def build_client() -> spotipy.Spotify:
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.environ.get("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")
    if not client_id or not client_secret:
        raise RuntimeError("Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET")
    scopes = [
        "user-read-playback-state",
        "user-modify-playback-state",
        "user-read-currently-playing",
        "playlist-read-private",
        "playlist-modify-private",
        "playlist-modify-public",
    ]
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=" ".join(scopes),
        cache_path=os.environ.get("SPOTIFY_TOKEN_CACHE", ".spotify_token_cache"),
        open_browser=True,
        show_dialog=False,
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    sp = build_client()
    res = sp.search(q=args.query, type="track", limit=max(1, min(args.limit, 50)))
    items = res.get("tracks", {}).get("items", [])
    simplified = []
    for t in items:
        simplified.append(
            {
                "name": t.get("name"),
                "uri": t.get("uri"),
                "id": t.get("id"),
                "artists": ", ".join(a.get("name") for a in t.get("artists", [])),
                "album": t.get("album", {}).get("name"),
                "duration_ms": t.get("duration_ms"),
            }
        )
    print(json.dumps(simplified, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


