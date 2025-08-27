#!/usr/bin/env python3

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_spotify_auth():
    """Test Spotify authentication and get playlists"""
    print("Testing Spotify OAuth authentication...")
    
    # Check environment
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.environ.get("SPOTIFY_REDIRECT_URI")
    
    print(f"Client ID present: {bool(client_id)}")
    print(f"Client Secret present: {bool(client_secret)}")
    print(f"Redirect URI: {redirect_uri}")
    
    # Set redirect URI to localhost for proper OAuth flow
    os.environ["SPOTIFY_REDIRECT_URI"] = "http://localhost:8888/callback"
    print(f"Using redirect URI: {os.environ['SPOTIFY_REDIRECT_URI']}")
    
    try:
        # Import and test the build_spotify_client function
        from mcp_spotify import _build_spotify_client
        
        print("\nAttempting to create Spotify client...")
        print("This may open a browser for OAuth authentication...")
        
        sp = _build_spotify_client()
        print("✓ Spotify client created successfully!")
        
        # Test getting current user playlists
        print("\nTesting playlist retrieval...")
        playlists = sp.current_user_playlists(limit=5)
        
        print(f"Found {len(playlists['items'])} playlists:")
        for playlist in playlists['items']:
            print(f"  - {playlist['name']} ({playlist['tracks']['total']} tracks)")
            
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_spotify_auth()
    if success:
        print("\n✓ Authentication and API test successful!")
        print("Your MCP server should now be able to interact with Spotify.")
    else:
        print("\n✗ Authentication failed. Please check your credentials and try again.")