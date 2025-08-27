#!/usr/bin/env python3

import os
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def build_spotify_client():
    """Create and return an authenticated Spotipy client using OAuth."""
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.environ.get("SPOTIFY_REDIRECT_URI", "https://spotify-3ti5.onrender.com")

    if not client_id or not client_secret:
        raise RuntimeError(
            "Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET environment variables."
        )

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

def list_playlists(limit=20, offset=0):
    """List current user's playlists."""
    sp = build_spotify_client()
    res = sp.current_user_playlists(limit=max(1, min(limit, 50)), offset=max(0, offset))
    items = res.get("items", [])
    return [
        {
            "name": p.get("name"),
            "id": p.get("id"),
            "uri": p.get("uri"),
            "tracks_total": p.get("tracks", {}).get("total"),
        }
        for p in items
    ]

if __name__ == "__main__":
    try:
        playlists = list_playlists()
        print(json.dumps(playlists, indent=2))
    except Exception as e:
        print(f"Error: {e}")