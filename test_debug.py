#!/usr/bin/env python3

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mcp_spotify

def test_debug_logging():
    print("Testing debug logging functionality...")
    
    # Test ping function directly
    print("\n1. Testing ping()...")
    try:
        # Call the original function before it was decorated
        result = {"status": "ok"}  # Simulate ping
        print(f"Ping result: {result}")
        
        # Test with actual decorated function by importing the module
        import importlib
        importlib.reload(mcp_spotify)
        
        # Access the function from the module's globals
        ping_original = None
        for name, obj in mcp_spotify.__dict__.items():
            if name == 'ping' and hasattr(obj, '__call__'):
                # This is the decorated function
                ping_original = obj.func if hasattr(obj, 'func') else obj._func
                break
                
        if ping_original:
            print("Found original ping function, testing debug wrapper...")
            # This should trigger debug logging
            result = ping_original()
            print(f"Debug ping result: {result}")
        else:
            print("Could not find original ping function")
            
    except Exception as e:
        print(f"Ping error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test health function  
    print("\n2. Testing health()...")
    try:
        # Manually call the health logic
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
    except Exception as e:
        print(f"Health error: {e}")
    
    print("\n3. Check debug log file...")
    if os.path.exists('mcp_spotify_debug.log'):
        print("Debug log file created successfully!")
        with open('mcp_spotify_debug.log', 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"Log content preview:\n{content[-500:]}")  # Last 500 chars
    else:
        print("No debug log file found")

if __name__ == "__main__":
    test_debug_logging()