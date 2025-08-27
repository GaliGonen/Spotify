import os
import json
import logging
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional
from functools import wraps

from fastmcp import FastMCP
import spotipy
from spotipy.oauth2 import SpotifyOAuth


# Configure debug logging with UTF-8 encoding
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('mcp_spotify_debug.log', encoding='utf-8')
    ]
)
# Skip console encoding fix for MCP stdio mode
logger = logging.getLogger(__name__)

# Debug decorator for all tool functions
def debug_tool(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.info(f"TOOL CALL: {func_name}")
        logger.debug(f"Args: {args}, Kwargs: {kwargs}")
        
        try:
            start_time = datetime.now()
            result = func(*args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"TOOL SUCCESS: {func_name} (took {duration:.2f}s)")
            logger.debug(f"Response: {json.dumps(result, indent=2, default=str)}")
            return result
            
        except Exception as e:
            logger.error(f"TOOL ERROR: {func_name} - {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Return error info instead of raising
            return {
                "error": True,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "function": func_name,
                "timestamp": datetime.now().isoformat()
            }
    return wrapper

def _build_spotify_client() -> spotipy.Spotify:
    """Create and return an authenticated Spotipy client using OAuth.

    Requires environment variables:
    - SPOTIFY_CLIENT_ID
    - SPOTIFY_CLIENT_SECRET
    - SPOTIFY_REDIRECT_URI (defaults to https://spotify-3ti5.onrender.com)
    """
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.environ.get("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback")

    logger.debug(f"Auth check - CLIENT_ID present: {bool(client_id)}, CLIENT_SECRET present: {bool(client_secret)}")
    
    if not client_id or not client_secret:
        error_msg = "Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET environment variables."
        logger.error(f"Authentication error: {error_msg}")
        raise RuntimeError(error_msg)

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
    logger.info(f"Creating Spotify client with redirect_uri: {redirect_uri}")
    logger.debug(f"Scopes: {' '.join(scopes)}")
    logger.debug(f"Token cache path: {os.environ.get('SPOTIFY_TOKEN_CACHE', '.spotify_token_cache')}")
    
    try:
        spotify_client = spotipy.Spotify(auth_manager=auth_manager)
        logger.info("Spotify client created successfully")
        return spotify_client
    except Exception as e:
        logger.error(f"Failed to create Spotify client: {e}")
        raise


server = FastMCP("spotify")

# Log available tools on import
logger.info("Available tools: ping, health, current_playback, play, pause, next_track, previous_track, search_tracks, list_playlists, add_to_playlist, transfer_playback_to_device, list_devices")


@server.tool()
@debug_tool
def ping() -> Dict[str, Any]:
    """Lightweight connectivity test that doesn't touch Spotify APIs."""
    return {"status": "ok"}


@server.tool()
@debug_tool
def health() -> Dict[str, Any]:
    """Report server/env health without performing Spotify network calls."""
    token_cache_path = os.environ.get("SPOTIFY_TOKEN_CACHE", ".spotify_token_cache")
    return {
        "python_executable": os.environ.get("PYTHON_EXECUTABLE", ""),
        "cwd": os.getcwd(),
        "env_present": {
            "SPOTIFY_CLIENT_ID": bool(os.environ.get("SPOTIFY_CLIENT_ID")),
            "SPOTIFY_CLIENT_SECRET": bool(os.environ.get("SPOTIFY_CLIENT_SECRET")),
            "SPOTIFY_REDIRECT_URI": bool(os.environ.get("SPOTIFY_REDIRECT_URI")),
        },
        "token_cache_exists": os.path.exists(token_cache_path),
        "token_cache_path": token_cache_path,
    }


@server.tool()
@debug_tool
def current_playback() -> Dict[str, Any]:
    """Get current playback state (device, context, item, is_playing)."""
    sp = _build_spotify_client()
    state = sp.current_playback()
    return state or {}


@server.tool()
@debug_tool
def play(
    uri: Optional[str] = None,
    query: Optional[str] = None,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Start/resume playback.

    - If `uri` is provided, attempts to play that track/album/playlist URI.
    - If `query` is provided (and no `uri`), searches for a track and plays the top result.
    - If neither provided, resumes current playback.
    """
    sp = _build_spotify_client()

    if uri:
        # Heuristic: if it's a track, use uris; if it's a context (album/playlist/artist), use context_uri
        if ":track:" in uri:
            sp.start_playback(device_id=device_id, uris=[uri])
        else:
            sp.start_playback(device_id=device_id, context_uri=uri)
        return {"status": "started", "source": uri}

    if query:
        results = sp.search(q=query, type="track", limit=1)
        tracks = results.get("tracks", {}).get("items", [])
        if not tracks:
            return {"status": "no_results", "query": query}
        top_uri = tracks[0]["uri"]
        sp.start_playback(device_id=device_id, uris=[top_uri])
        return {"status": "started", "query": query, "uri": top_uri}

    # Resume existing context
    sp.start_playback(device_id=device_id)
    return {"status": "resumed"}


@server.tool()
@debug_tool
def pause(device_id: Optional[str] = None) -> Dict[str, Any]:
    """Pause playback."""
    sp = _build_spotify_client()
    sp.pause_playback(device_id=device_id)
    return {"status": "paused"}


@server.tool()
@debug_tool
def next_track(device_id: Optional[str] = None) -> Dict[str, Any]:
    """Skip to next track."""
    sp = _build_spotify_client()
    sp.next_track(device_id=device_id)
    return {"status": "skipped"}


@server.tool()
@debug_tool
def previous_track(device_id: Optional[str] = None) -> Dict[str, Any]:
    """Skip to previous track."""
    sp = _build_spotify_client()
    sp.previous_track(device_id=device_id)
    return {"status": "skipped_back"}


@server.tool()
@debug_tool
def search_tracks(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search for tracks and return basic metadata and URIs."""
    sp = _build_spotify_client()
    res = sp.search(q=query, type="track", limit=max(1, min(limit, 50)))
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
    return simplified


@server.tool()
@debug_tool
def list_playlists(limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """List current user's playlists."""
    sp = _build_spotify_client()
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


@server.tool()
@debug_tool
def add_to_playlist(playlist_id: str, track_uri: str) -> Dict[str, Any]:
    """Add a track URI to a playlist by ID."""
    sp = _build_spotify_client()
    sp.playlist_add_items(playlist_id, [track_uri])
    return {"status": "added", "playlist_id": playlist_id, "track_uri": track_uri}


@server.tool()
@debug_tool
def transfer_playback_to_device(device_id: str, play: bool = True) -> Dict[str, Any]:
    """Transfer playback to a specific device ID."""
    sp = _build_spotify_client()
    sp.transfer_playback(device_id=device_id, force_play=play)
    return {"status": "transferred", "device_id": device_id, "play": play}


@server.tool()
@debug_tool
def list_devices() -> List[Dict[str, Any]]:
    """List available Spotify Connect devices."""
    sp = _build_spotify_client()
    res = sp.devices()
    return res.get("devices", [])


if __name__ == "__main__":
    logger.info("Starting Spotify MCP Server")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Python executable: {sys.executable}")
    
    # Log environment status
    env_status = {
        "SPOTIFY_CLIENT_ID": bool(os.environ.get("SPOTIFY_CLIENT_ID")),
        "SPOTIFY_CLIENT_SECRET": bool(os.environ.get("SPOTIFY_CLIENT_SECRET")),
        "SPOTIFY_REDIRECT_URI": os.environ.get("SPOTIFY_REDIRECT_URI", "Not set"),
        "SPOTIFY_TOKEN_CACHE": os.environ.get("SPOTIFY_TOKEN_CACHE", ".spotify_token_cache")
    }
    logger.info(f"Environment: {json.dumps(env_status, indent=2)}")
    
    try:
        # FastMCP runs as stdio-based server, not HTTP
        server.run()
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        sys.exit(1)


