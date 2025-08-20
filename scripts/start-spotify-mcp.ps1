param(
  [switch]$PersistWithSetx
)

function Ensure-Module($Name) {
  if (-not (Get-Module -ListAvailable -Name $Name)) {
    try {
      Install-Module -Name $Name -Scope CurrentUser -Force -AllowClobber -Confirm:$false -ErrorAction Stop
    } catch {
      Write-Host "Could not install module $Name. Continuing without it." -ForegroundColor Yellow
    }
  }
  Import-Module -Name $Name -ErrorAction SilentlyContinue | Out-Null
}

function Read-PlainFromSecure([SecureString]$s) {
  $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($s)
  try { [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr) } finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
}

$clientId = $null
$clientSecret = $null
$redirectUri = $null

# Try SecretManagement first
Ensure-Module Microsoft.PowerShell.SecretManagement
Ensure-Module Microsoft.PowerShell.SecretStore

$secretMgmtAvailable = (Get-Module -ListAvailable -Name Microsoft.PowerShell.SecretManagement) -ne $null
if ($secretMgmtAvailable) {
  if (-not (Get-SecretVault -Name SpotifySecrets -ErrorAction SilentlyContinue)) {
    Register-SecretVault -Name SpotifySecrets -ModuleName Microsoft.PowerShell.SecretStore -DefaultVault -ErrorAction SilentlyContinue | Out-Null
  }

  $clientId = Get-Secret -Name SPOTIFY_CLIENT_ID -AsPlainText -Vault SpotifySecrets -ErrorAction SilentlyContinue
  if (-not $clientId) {
    $clientId = Read-Host "Enter SPOTIFY_CLIENT_ID"
    Set-Secret -Name SPOTIFY_CLIENT_ID -Secret $clientId -Vault SpotifySecrets | Out-Null
  }

  $clientSecretPlain = Get-Secret -Name SPOTIFY_CLIENT_SECRET -AsPlainText -Vault SpotifySecrets -ErrorAction SilentlyContinue
  if (-not $clientSecretPlain) {
    $sec = Read-Host "Enter SPOTIFY_CLIENT_SECRET" -AsSecureString
    $clientSecretPlain = Read-PlainFromSecure $sec
    Set-Secret -Name SPOTIFY_CLIENT_SECRET -Secret $clientSecretPlain -Vault SpotifySecrets | Out-Null
  }
  $clientSecret = $clientSecretPlain

  $redirectUri = Get-Secret -Name SPOTIFY_REDIRECT_URI -AsPlainText -Vault SpotifySecrets -ErrorAction SilentlyContinue
  if (-not $redirectUri) {
    $redirectUri = Read-Host "Enter SPOTIFY_REDIRECT_URI (default http://localhost:8888/callback)"
    if (-not $redirectUri) { $redirectUri = "http://localhost:8888/callback" }
    Set-Secret -Name SPOTIFY_REDIRECT_URI -Secret $redirectUri -Vault SpotifySecrets | Out-Null
  }
}

if (-not $clientId -or -not $clientSecret) {
  Write-Host "Falling back to prompting (SecretManagement not available)." -ForegroundColor Yellow
  $clientId = if ($env:SPOTIFY_CLIENT_ID) { $env:SPOTIFY_CLIENT_ID } else { Read-Host "Enter SPOTIFY_CLIENT_ID" }
  if ($env:SPOTIFY_CLIENT_SECRET) {
    $clientSecret = $env:SPOTIFY_CLIENT_SECRET
  } else {
    $sec = Read-Host "Enter SPOTIFY_CLIENT_SECRET" -AsSecureString
    $clientSecret = Read-PlainFromSecure $sec
  }
  $redirectUri = if ($env:SPOTIFY_REDIRECT_URI) { $env:SPOTIFY_REDIRECT_URI } else { Read-Host "Enter SPOTIFY_REDIRECT_URI (default http://localhost:8888/callback)" }
  if (-not $redirectUri) { $redirectUri = "http://localhost:8888/callback" }

  if ($PersistWithSetx) {
    Write-Host "Persisting variables with setx (stored as plain text in user env)." -ForegroundColor Yellow
    setx SPOTIFY_CLIENT_ID "$clientId" | Out-Null
    setx SPOTIFY_CLIENT_SECRET "$clientSecret" | Out-Null
    setx SPOTIFY_REDIRECT_URI "$redirectUri" | Out-Null
    Write-Host "Persisted. You must restart Cursor and your terminal for changes to take effect."
  }
}

$env:SPOTIFY_CLIENT_ID = $clientId
$env:SPOTIFY_CLIENT_SECRET = $clientSecret
$env:SPOTIFY_REDIRECT_URI = $redirectUri

Write-Host "Launching Spotify MCP server..."
python mcp_spotify.py


