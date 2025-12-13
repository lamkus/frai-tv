# Deploy Script fuer FRai.TV Frontend
# ACHTUNG: Deployed NUR in /FRai.TV/ Unterordner!
# SECURITY:
# - Keine festen Hosts/User im Repo: setze ENV Vars lokal.
# - Default: SSH Host Key Fingerprint erforderlich (kein blindes AcceptAnyHostKey).

param(
    [switch]$Insecure
)

$Server = $env:STRATO_SFTP_HOST
$User = $env:STRATO_SFTP_USER
$RemotePath = $env:STRATO_SFTP_REMOTE_PATH
$LocalPath = "d:\remaike.TV\code\frontend\dist\*"

if (-not $Server -or -not $User -or -not $RemotePath) {
    Write-Host "[ERROR] Missing deployment env vars." -ForegroundColor Red
    Write-Host "Set locally (example):" -ForegroundColor Yellow
    Write-Host "  `$env:STRATO_SFTP_HOST='YOUR_STRATO_HOST'" -ForegroundColor Cyan
    Write-Host "  `$env:STRATO_SFTP_USER='YOUR_STRATO_USER'" -ForegroundColor Cyan
    Write-Host "  `$env:STRATO_SFTP_REMOTE_PATH='/FRai.TV/'" -ForegroundColor Cyan
    Write-Host "Optional (recommended):`n  `$env:STRATO_SSH_HOSTKEY='ssh-ed25519 256 ...'" -ForegroundColor DarkGray
    Write-Host "Run with -Insecure only if you understand the risk." -ForegroundColor DarkGray
    exit 2
}

# SICHERHEITSCHECK: Nie root löschen!
if ($RemotePath -eq "/" -or $RemotePath -eq "") {
    Write-Host "[FATAL] RemotePath darf NICHT root sein! Abbruch." -ForegroundColor Red
    exit 1
}

# Passwort-Datei (verschluesselt, nur fuer aktuellen User lesbar)
$CredFile = "$env:USERPROFILE\.strato_cred.xml"

# Pruefen ob Credentials gespeichert sind
if (Test-Path $CredFile) {
    $Cred = Import-Clixml $CredFile
    Write-Host "Gespeicherte Credentials gefunden" -ForegroundColor Green
} else {
    Write-Host "Bitte Strato-Passwort eingeben (wird verschluesselt gespeichert):" -ForegroundColor Yellow
    $Cred = Get-Credential -UserName $User -Message "Strato SFTP Passwort"
    $Cred | Export-Clixml $CredFile
    Write-Host "Credentials gespeichert in $CredFile" -ForegroundColor Green
}

# Build erstellen
Write-Host ""
Write-Host "[BUILD] Building Frontend..." -ForegroundColor Cyan
Push-Location "d:\remaike.TV\code\frontend"
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Build fehlgeschlagen!" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

# WinSCP Assembly fuer SFTP
$WinSCPPath = "$env:LOCALAPPDATA\Programs\WinSCP\WinSCPnet.dll"
if (-not (Test-Path $WinSCPPath)) {
    $WinSCPPath = "${env:ProgramFiles(x86)}\WinSCP\WinSCPnet.dll"
}
if (-not (Test-Path $WinSCPPath)) {
    $WinSCPPath = "$env:ProgramFiles\WinSCP\WinSCPnet.dll"
}

Write-Host ""
Write-Host "[UPLOAD] Uploading to Strato..." -ForegroundColor Cyan

if (Test-Path $WinSCPPath) {
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
        
        # Lösche ALLES (index.html + assets) vor Upload - verhindert Cache-Probleme
        Write-Host "  Cleaning old files..." -ForegroundColor Gray
        try {
            $session.RemoveFiles($RemotePath + "*").Check()
        } catch {
            Write-Host "  (No old files to clean)" -ForegroundColor DarkGray
        }
        
        $transferResult = $session.PutFiles($LocalPath, $RemotePath)
        $transferResult.Check()
        
        foreach ($transfer in $transferResult.Transfers) {
            Write-Host "  Uploaded: $($transfer.FileName)" -ForegroundColor Gray
        }
        
        Write-Host ""
        Write-Host "[SUCCESS] Upload erfolgreich via WinSCP!" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Upload fehlgeschlagen: $_" -ForegroundColor Red
        exit 1
    } finally {
        $session.Dispose()
    }
} else {
    # Fallback: Interaktiver SCP
    Write-Host "[INFO] WinSCP nicht gefunden, nutze SCP..." -ForegroundColor Yellow
    scp -r $LocalPath "${User}@${Server}:${RemotePath}"
}

Write-Host ""
Write-Host "[DONE] Deployment abgeschlossen!" -ForegroundColor Green
Write-Host "Website: https://www.frai.tv" -ForegroundColor Cyan
