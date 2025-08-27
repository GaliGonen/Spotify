#!/usr/bin/env python3

import json
import subprocess
import sys
import time

def test_mcp_server():
    print("Testing MCP server interaction...")
    
    # Start the MCP server as subprocess
    process = subprocess.Popen(
        [sys.executable, "mcp_spotify.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="C:\\Programming\\Spotify"
    )
    
    try:
        # Initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-10-07",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        print("Sending initialize request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Wait for response
        time.sleep(1)
        
        # Read response
        response = process.stdout.readline()
        if response:
            print(f"Response: {response.strip()}")
        
        # Test ping tool
        ping_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "ping",
                "arguments": {}
            }
        }
        
        print("Sending ping request...")
        process.stdin.write(json.dumps(ping_request) + "\n")
        process.stdin.flush()
        
        # Wait for response
        time.sleep(1)
        
        # Read response
        response = process.stdout.readline()
        if response:
            print(f"Ping response: {response.strip()}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        process.terminate()
        process.wait()
        
        # Check for stderr output
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"Server stderr: {stderr_output}")

if __name__ == "__main__":
    test_mcp_server()