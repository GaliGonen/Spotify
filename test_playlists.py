#!/usr/bin/env python3

import os
import sys

# Add current directory to path  
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_list_playlists():
    """Test listing playlists directly"""
    print("Testing playlist retrieval...")
    
    # Set loopback IP redirect URI (recommended over localhost)
    os.environ["SPOTIFY_REDIRECT_URI"] = "http://127.0.0.1:8888/callback"
    
    try:
        # Import the actual list_playlists function
        from mcp_spotify import _build_spotify_client
        
        # Build client  
        print("Creating Spotify client...")
        sp = _build_spotify_client()
        
        # Get playlists
        print("Fetching playlists...")
        res = sp.current_user_playlists(limit=10, offset=0)
        items = res.get("items", [])
        
        playlists = [
            {
                "name": p.get("name"),
                "id": p.get("id"), 
                "uri": p.get("uri"),
                "tracks_total": p.get("tracks", {}).get("total"),
            }
            for p in items
        ]
        
        print(f"\nFound {len(playlists)} playlists:")
        for i, playlist in enumerate(playlists, 1):
            print(f"{i}. {playlist['name']} - {playlist['tracks_total']} tracks")
            print(f"   URI: {playlist['uri']}")
        
        return playlists
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    playlists = test_list_playlists()
    if playlists:
        print(f"\nSuccess! Retrieved {len(playlists)} playlists from Spotify.")
        print("Your MCP server debug logging should show the authentication flow.")
    else:
        print("\nFailed to retrieve playlists.")