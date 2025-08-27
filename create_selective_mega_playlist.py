#!/usr/bin/env python3

import os
import sys
import time
import logging

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Disable spotipy debug logging to avoid Unicode issues
logging.getLogger('spotipy').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

def create_selective_mega_playlist():
    """Create a mega playlist from selected playlists"""
    print("Creating Mega Playlist from selected playlists...")
    
    # Set the environment variable to use localhost redirect
    os.environ["SPOTIFY_REDIRECT_URI"] = "http://127.0.0.1:8888/callback"
    
    try:
        from mcp_spotify import _build_spotify_client
        
        # Build client
        print("Connecting to Spotify...")
        sp = _build_spotify_client()
        
        # Get current user info
        user = sp.current_user()
        user_id = user['id']
        print(f"Hello {user['display_name']}!")
        
        # Step 1: Get all playlists and show them
        print("\nFetching your playlists...")
        all_playlists = []
        limit = 50
        offset = 0
        
        while True:
            res = sp.current_user_playlists(limit=limit, offset=offset)
            items = res.get("items", [])
            if not items:
                break
            all_playlists.extend(items)
            if len(items) < limit:
                break
            offset += limit
        
        # Filter to only user's own playlists
        own_playlists = [p for p in all_playlists if p['owner']['id'] == user_id]
        
        print(f"\nYour {len(own_playlists)} playlists:")
        for i, playlist in enumerate(own_playlists, 1):
            track_count = playlist['tracks']['total']
            playlist_name = playlist['name'].encode('ascii', errors='replace').decode('ascii')
            print(f"{i:2}. {playlist_name} - {track_count} tracks")
        
        # Step 2: Let user select playlists
        print(f"\nEnter the playlist numbers you want to include (e.g., 1,3,5-8,10):")
        print("Press Enter to include all playlists, or type 'q' to quit.")
        
        selection = input("Selection: ").strip()
        
        if selection.lower() == 'q':
            print("Cancelled.")
            return None
            
        if not selection:
            # Include all playlists
            selected_playlists = own_playlists
            print("Including all playlists.")
        else:
            # Parse selection
            selected_indices = set()
            for part in selection.split(','):
                if '-' in part:
                    # Range like 5-8
                    start, end = map(int, part.split('-'))
                    selected_indices.update(range(start, end + 1))
                else:
                    # Single number
                    selected_indices.add(int(part))
            
            # Convert to 0-based indices and get playlists
            selected_playlists = []
            for idx in sorted(selected_indices):
                if 1 <= idx <= len(own_playlists):
                    selected_playlists.append(own_playlists[idx - 1])
            
            print(f"Selected {len(selected_playlists)} playlists:")
            for playlist in selected_playlists:
                playlist_name = playlist['name'].encode('ascii', errors='replace').decode('ascii')
                print(f"  - {playlist_name} ({playlist['tracks']['total']} tracks)")
        
        if not selected_playlists:
            print("No playlists selected.")
            return None
        
        # Step 3: Collect tracks from selected playlists
        print(f"\nCollecting tracks from {len(selected_playlists)} playlists...")
        all_tracks = {}  # Use dict to avoid duplicates by track ID
        
        for i, playlist in enumerate(selected_playlists, 1):
            playlist_name = playlist['name'].encode('ascii', errors='replace').decode('ascii')
            playlist_id = playlist['id']
            track_count = playlist['tracks']['total']
            
            print(f"  {i}/{len(selected_playlists)} Processing '{playlist_name}' ({track_count} tracks)")
            
            # Get all tracks from this playlist
            tracks = []
            offset = 0
            while True:
                try:
                    results = sp.playlist_tracks(playlist_id, offset=offset, limit=100)
                    track_items = results.get('items', [])
                    if not track_items:
                        break
                    tracks.extend(track_items)
                    if len(track_items) < 100:
                        break
                    offset += 100
                    time.sleep(0.1)  # Rate limiting
                except Exception as e:
                    print(f"      Error fetching tracks: {e}")
                    break
            
            # Add tracks to our collection (avoiding duplicates)
            for item in tracks:
                track = item.get('track')
                if track and track.get('id') and track.get('type') == 'track':  # Only music tracks, not episodes
                    track_id = track['id']
                    if track_id not in all_tracks:
                        all_tracks[track_id] = {
                            'uri': track['uri'],
                            'name': track['name'],
                            'artists': ', '.join([a['name'] for a in track.get('artists', [])]),
                            'album': track.get('album', {}).get('name', 'Unknown')
                        }
            
            print(f"      Added tracks (Total unique: {len(all_tracks)})")
        
        if not all_tracks:
            print("No tracks found in selected playlists.")
            return None
        
        print(f"\nCollected {len(all_tracks)} unique tracks")
        
        # Step 4: Create new mega playlist
        mega_playlist_name = f"Mega Playlist - Selected ({len(all_tracks)} tracks)"
        print(f"\nCreating playlist: '{mega_playlist_name}'")
        
        try:
            mega_playlist = sp.user_playlist_create(
                user=user_id,
                name=mega_playlist_name,
                description=f"Auto-generated mega playlist containing {len(all_tracks)} unique tracks from {len(selected_playlists)} selected playlists. Created on {time.strftime('%Y-%m-%d')}"
            )
            
            mega_playlist_id = mega_playlist['id']
            print(f"Created playlist: {mega_playlist['external_urls']['spotify']}")
            
        except Exception as e:
            print(f"Failed to create playlist: {e}")
            return None
        
        # Step 5: Add tracks to mega playlist (in batches)
        print(f"\nAdding {len(all_tracks)} tracks to mega playlist...")
        track_uris = [track['uri'] for track in all_tracks.values()]
        
        # Spotify allows max 100 tracks per request
        batch_size = 100
        added_count = 0
        
        for i in range(0, len(track_uris), batch_size):
            batch = track_uris[i:i + batch_size]
            try:
                sp.playlist_add_items(mega_playlist_id, batch)
                added_count += len(batch)
                print(f"  Added batch {i//batch_size + 1}: {added_count}/{len(track_uris)} tracks")
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"  Error adding batch: {e}")
                continue
        
        print(f"\nSUCCESS! Created mega playlist with {added_count} tracks!")
        print(f"Playlist URL: {mega_playlist['external_urls']['spotify']}")
        print(f"Playlist ID: {mega_playlist_id}")
        
        # Show some stats
        print(f"\nStatistics:")
        print(f"  • Processed {len(selected_playlists)} playlists")
        print(f"  • Found {len(all_tracks)} unique tracks")
        print(f"  • Successfully added {added_count} tracks")
        print(f"  • Playlist name: {mega_playlist_name}")
        
        return mega_playlist_id
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    playlist_id = create_selective_mega_playlist()
    if playlist_id:
        print("\nYour selective mega playlist is ready to enjoy!")
    else:
        print("\nFailed to create mega playlist.")