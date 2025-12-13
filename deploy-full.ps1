# =============================================================================
# FULL STACK DEPLOY SCRIPT für remAIke.TV
# Deployed Frontend + Backend auf Strato VPS
# =============================================================================
# SECURITY:
# - Keine festen Hosts/User im Repo: setze ENV Vars lokal.
# - Default: SSH Host Key Fingerprint erforderlich (kein blindes AcceptAnyHostKey).

param(
    [switch]$Insecure
)

$Server = $env:STRATO_SFTP_HOST
$User = $env:STRATO_SFTP_USER
$ProjectRoot = "d:\remaike.TV"

if (-not $Server -or -not $User) {
    Write-Host "[ERROR] Missing deployment env vars." -ForegroundColor Red
    Write-Host "Set locally (example):" -ForegroundColor Yellow
    Write-Host "  `$env:STRATO_SFTP_HOST='YOUR_STRATO_HOST'" -ForegroundColor Cyan
    Write-Host "  `$env:STRATO_SFTP_USER='YOUR_STRATO_USER'" -ForegroundColor Cyan
    Write-Host "Optional (recommended):`n  `$env:STRATO_SSH_HOSTKEY='ssh-ed25519 256 ...'" -ForegroundColor DarkGray
    Write-Host "Run with -Insecure only if you understand the risk." -ForegroundColor DarkGray
    exit 2
}

# Remote-Pfade auf Strato (anpassen falls noetig)
$RemoteFrontend = "/"                           # Frontend: Document Root
$RemoteBackend = "/backend/"                    # Backend: Unterordner

# Passwort-Datei (verschluesselt)
$CredFile = "$env:USERPROFILE\.strato_cred.xml"

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   remAIke.TV Full-Stack Deployment" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Credentials laden/speichern
if (Test-Path $CredFile) {
    $Cred = Import-Clixml $CredFile
    Write-Host "[OK] Gespeicherte Credentials gefunden" -ForegroundColor Green
} else {
    Write-Host "[?] Bitte Strato-Passwort eingeben:" -ForegroundColor Yellow
    $Cred = Get-Credential -UserName $User -Message "Strato SFTP Passwort"
    $Cred | Export-Clixml $CredFile
    Write-Host "[OK] Credentials gespeichert" -ForegroundColor Green
}

# =============================================================================
# STEP 1: Frontend Build
# =============================================================================
Write-Host ""
Write-Host "[1/4] Building Frontend..." -ForegroundColor Cyan
Push-Location "$ProjectRoot\code\frontend"
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Frontend Build fehlgeschlagen!" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location
Write-Host "[OK] Frontend Build erfolgreich" -ForegroundColor Green

# =============================================================================
# STEP 2: Backend vorbereiten (node_modules ausschliessen)
# =============================================================================
Write-Host ""
Write-Host "[2/4] Preparing Backend..." -ForegroundColor Cyan

$BackendPath = "$ProjectRoot\code\backend"
$BackendTempPath = "$env:TEMP\remaike-backend-deploy"

# Temp-Ordner erstellen
if (Test-Path $BackendTempPath) {
    Remove-Item -Recurse -Force $BackendTempPath
}
New-Item -ItemType Directory -Path $BackendTempPath | Out-Null

# Backend-Dateien kopieren (OHNE node_modules)
$filesToCopy = @(
    "package.json",
    "package-lock.json",
    "ecosystem.config.cjs",
    "start.js",
    "prisma.config.ts"
)

foreach ($file in $filesToCopy) {
    $src = Join-Path $BackendPath $file
    if (Test-Path $src) {
        Copy-Item $src $BackendTempPath
        Write-Host "  + $file" -ForegroundColor Gray
    }
}

# src/ Ordner kopieren
if (Test-Path "$BackendPath\src") {
    Copy-Item -Recurse "$BackendPath\src" "$BackendTempPath\src"
    Write-Host "  + src/" -ForegroundColor Gray
}

# prisma/ Ordner kopieren
if (Test-Path "$BackendPath\prisma") {
    Copy-Item -Recurse "$BackendPath\prisma" "$BackendTempPath\prisma"
    Write-Host "  + prisma/" -ForegroundColor Gray
}

Write-Host "[OK] Backend vorbereitet (ohne node_modules)" -ForegroundColor Green

# =============================================================================
# STEP 3: WinSCP Upload
# =============================================================================
Write-Host ""
Write-Host "[3/4] Uploading to Strato..." -ForegroundColor Cyan

# WinSCP finden
$WinSCPPath = @(
    "$env:LOCALAPPDATA\Programs\WinSCP\WinSCPnet.dll",
    "${env:ProgramFiles(x86)}\WinSCP\WinSCPnet.dll",
    "$env:ProgramFiles\WinSCP\WinSCPnet.dll"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $WinSCPPath) {
    Write-Host "[ERROR] WinSCP nicht gefunden! Bitte installieren:" -ForegroundColor Red
    Write-Host "        https://winscp.net/eng/download.php" -ForegroundColor Yellow
    exit 1
}

Add-Type -Path $WinSCPPath

$sessionOptions = New-Object WinSCP.SessionOptions -Property @{
    Protocol = [WinSCP.Protocol]::Sftp
    HostName = $Server
    UserName = $User
    Password = $Cred.GetNetworkCredential().Password
    GiveUpSecurityAndAcceptAnySshHostKey = $Insecure
}

if (-not $Insecure) {
    $fp = $env:STRATO_SSH_HOSTKEY
    if (-not $fp) {
        Write-Host "[ERROR] STRATO_SSH_HOSTKEY not set. Refusing insecure SSH host key acceptance." -ForegroundColor Red
        Write-Host "Set `$env:STRATO_SSH_HOSTKEY to the server host key fingerprint, or re-run with -Insecure." -ForegroundColor Yellow
        exit 2
    }
    $sessionOptions.SshHostKeyFingerprint = $fp
}

$session = New-Object WinSCP.Session
try {
    $session.Open($sessionOptions)
    
    # ----- Frontend Upload -----
    Write-Host ""
    Write-Host "  Uploading Frontend..." -ForegroundColor Yellow
    
    # Alte Frontend-Dateien loeschen (ausser backend/)
    try {
        $remoteFiles = $session.EnumerateRemoteFiles($RemoteFrontend, "*", [WinSCP.EnumerationOptions]::None)
        foreach ($file in $remoteFiles) {
            if ($file.Name -ne "backend" -and $file.Name -ne ".htaccess") {
                $session.RemoveFiles($RemoteFrontend + $file.Name).Check()
            }
        }
    } catch {
        Write-Host "  (Cleanup skipped)" -ForegroundColor DarkGray
    }
    
    # Frontend hochladen
    $frontendResult = $session.PutFiles("$ProjectRoot\code\frontend\dist\*", $RemoteFrontend)
    $frontendResult.Check()
    Write-Host "  [OK] Frontend uploaded ($($frontendResult.Transfers.Count) files)" -ForegroundColor Green
    
    # ----- Backend Upload -----
    Write-Host ""
    Write-Host "  Uploading Backend..." -ForegroundColor Yellow
    
    # Backend-Ordner erstellen falls nicht vorhanden
    if (-not $session.FileExists($RemoteBackend)) {
        $session.CreateDirectory($RemoteBackend)
    }
    
    # Backend hochladen
    $backendResult = $session.PutFiles("$BackendTempPath\*", $RemoteBackend, $false, $null)
    $backendResult.Check()
    Write-Host "  [OK] Backend uploaded ($($backendResult.Transfers.Count) files)" -ForegroundColor Green
    
} catch {
    Write-Host "[ERROR] Upload fehlgeschlagen: $_" -ForegroundColor Red
    exit 1
} finally {
    $session.Dispose()
}

# Temp aufräumen
Remove-Item -Recurse -Force $BackendTempPath

# =============================================================================
# STEP 4: Anweisungen für Server-Setup
# =============================================================================
Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "   UPLOAD ERFOLGREICH!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "[NEXT STEPS] SSH auf Strato und Backend starten:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. SSH verbinden:" -ForegroundColor White
Write-Host "     ssh ${User}@${Server}" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Backend Dependencies installieren:" -ForegroundColor White
Write-Host "     cd /backend" -ForegroundColor Cyan
Write-Host "     npm install --production" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. .env Datei erstellen:" -ForegroundColor White
Write-Host "     nano .env" -ForegroundColor Cyan
Write-Host "     # NODE_ENV=production" -ForegroundColor DarkGray
Write-Host "     # PORT=4000" -ForegroundColor DarkGray
Write-Host "     # DATABASE_URL=postgres://..." -ForegroundColor DarkGray
Write-Host "     # YOUTUBE_API_KEY=YOUR_YOUTUBE_API_KEY" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  4. Prisma Migration (falls DB vorhanden):" -ForegroundColor White
Write-Host "     npx prisma migrate deploy" -ForegroundColor Cyan
Write-Host ""
Write-Host "  5. Backend mit PM2 starten:" -ForegroundColor White
Write-Host "     pm2 start ecosystem.config.cjs --env production" -ForegroundColor Cyan
Write-Host "     pm2 save" -ForegroundColor Cyan
Write-Host "     pm2 startup" -ForegroundColor Cyan
Write-Host ""
Write-Host "  6. In Plesk nginx Proxy konfigurieren:" -ForegroundColor White
Write-Host "     -> Siehe installation/plesk_nginx_directives.conf" -ForegroundColor Gray
Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "Website: https://www.frai.tv" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Green
