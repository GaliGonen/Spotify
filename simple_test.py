#!/usr/bin/env python3

import os
import sys

# Simple test without running as MCP server
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_functions():
    print("Testing individual functions...")
    
    # Test health function
    print("\nTesting health()...")
    token_cache_path = os.environ.get("SPOTIFY_TOKEN_CACHE", ".spotify_token_cache")
    result = {
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
    print(f"Health result: {result}")
    
    # Show environment status
    print(f"\nEnvironment Status:")
    print(f"  SPOTIFY_CLIENT_ID: {'✓' if os.environ.get('SPOTIFY_CLIENT_ID') else '✗'}")
    print(f"  SPOTIFY_CLIENT_SECRET: {'✓' if os.environ.get('SPOTIFY_CLIENT_SECRET') else '✗'}")
    print(f"  SPOTIFY_REDIRECT_URI: {os.environ.get('SPOTIFY_REDIRECT_URI', 'Not set')}")
    print(f"  Token cache exists: {'✓' if os.path.exists(token_cache_path) else '✗'}")

if __name__ == "__main__":
    test_functions()