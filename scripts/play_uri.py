import os
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
    parser.add_argument("--uri", required=True)
    parser.add_argument("--device-id")
    args = parser.parse_args()

    sp = build_client()
    if ":track:" in args.uri:
        sp.start_playback(device_id=args.device_id, uris=[args.uri])
    else:
        sp.start_playback(device_id=args.device_id, context_uri=args.uri)
    print("started", args.uri)


if __name__ == "__main__":
    main()


