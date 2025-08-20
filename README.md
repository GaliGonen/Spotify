# Spotify

## MCP Spotify Server (Python)

This project includes a simple MCP server exposing Spotify controls via tools, powered by `fastmcp` and `spotipy`.

### Prerequisites

- Python 3.10+
- Spotify Premium account
- Spotify Developer App (Client ID/Secret) at `https://developer.spotify.com/dashboard/`

Set Redirect URI in your Spotify app to `http://localhost:8888/callback` (or set your own and export it as `SPOTIFY_REDIRECT_URI`).

### Install

```bash
pip install -r requirements.txt
```

### Environment Variables

Set these before running the server:

- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`
- `SPOTIFY_REDIRECT_URI` (optional, default: `http://localhost:8888/callback`)
- `SPOTIFY_TOKEN_CACHE` (optional, default: `.spotify_token_cache`)

On Windows PowerShell:

```powershell
$env:SPOTIFY_CLIENT_ID = "your_client_id"
$env:SPOTIFY_CLIENT_SECRET = "your_client_secret"
$env:SPOTIFY_REDIRECT_URI = "http://localhost:8888/callback"
```

### Run the MCP server

```bash
python mcp_spotify.py
```

On first run, your browser will open to authorize Spotify scopes. Tokens are cached in `.spotify_token_cache`.

### Connect in Cursor (MCP)

Add to your Cursor MCP configuration (Settings → MCP):

```json
{
  "mcpServers": {
    "spotify": {
      "command": "python",
      "args": ["mcp_spotify.py"],
      "env": {
        "SPOTIFY_CLIENT_ID": "${env:SPOTIFY_CLIENT_ID}",
        "SPOTIFY_CLIENT_SECRET": "${env:SPOTIFY_CLIENT_SECRET}",
        "SPOTIFY_REDIRECT_URI": "${env:SPOTIFY_REDIRECT_URI}"
      }
    }
  }
}
```

After adding, restart Cursor or reload MCP. You should see tools like `current_playback`, `play`, `pause`, `search_tracks`, etc.
