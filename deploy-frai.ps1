# =============================================================================
# DEPLOY frai.tv — Clean Projector Frontend
# Builds and uploads the frai-tv project to Checkdomain
# =============================================================================
param([switch]$Insecure, [switch]$SkipBuild)

$Server  = if ($env:CHECKDOMAIN_FTP_HOST) { $env:CHECKDOMAIN_FTP_HOST } else { "host254.checkdomain.de" }
$User    = if ($env:CHECKDOMAIN_FTP_USER) { $env:CHECKDOMAIN_FTP_USER } else { "rnhszswb" }
$Project = "D:\remaike.TV\code\frai-tv"
$DistDir = "$Project\dist"
$Remote  = "/frai.tv/"

# ── Credentials ──────────────────────────────────────────────
$CredFile = "$env:USERPROFILE\.checkdomain_cred.xml"
if (Test-Path $CredFile) {
    $Cred = Import-Clixml $CredFile
    Write-Host "[OK] Credentials loaded" -ForegroundColor Green
} else {
    $Cred = Get-Credential -UserName $User -Message "Checkdomain FTP Password"
    $Cred | Export-Clixml $CredFile
    Write-Host "[OK] Credentials saved" -ForegroundColor Green
}

# ── Build ────────────────────────────────────────────────────
if (-not $SkipBuild) {
    Write-Host "`n[1/3] Building frai-tv..." -ForegroundColor Cyan
    Push-Location $Project

    # Generate static watch pages first
    node scripts/generate-watch-pages.mjs

    # Generate sitemap first
    node scripts/generate-sitemap.mjs
    
    # Build
    npx vite build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Build failed!" -ForegroundColor Red
        Pop-Location; exit 1
    }
    Pop-Location
    Write-Host "[OK] Build done" -ForegroundColor Green
} else {
    Write-Host "`n[1/3] Skipping build (--SkipBuild)" -ForegroundColor Yellow
}

# Verify dist
if (-not (Test-Path "$DistDir\index.html")) {
    Write-Host "[ERROR] dist/index.html not found!" -ForegroundColor Red
    exit 1
}

$files = Get-ChildItem -Recurse -File $DistDir
Write-Host "[OK] $($files.Count) files ready to deploy" -ForegroundColor Green

# ── Upload ───────────────────────────────────────────────────
Write-Host "`n[2/3] Uploading to $Server..." -ForegroundColor Cyan

$WinSCPPath = @(
    "$env:LOCALAPPDATA\Programs\WinSCP\WinSCPnet.dll",
    "${env:ProgramFiles(x86)}\WinSCP\WinSCPnet.dll",
    "$env:ProgramFiles\WinSCP\WinSCPnet.dll"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $WinSCPPath) {
    Write-Host "[ERROR] WinSCP not found!" -ForegroundColor Red
    exit 1
}

Add-Type -Path $WinSCPPath

$so = New-Object WinSCP.SessionOptions
$so.Protocol = [WinSCP.Protocol]::Ftp
$so.FtpSecure = [WinSCP.FtpSecure]::Explicit
$so.HostName = $Server
$so.UserName = $User
$so.Password = $Cred.GetNetworkCredential().Password
$so.GiveUpSecurityAndAcceptAnyTlsHostCertificate = $true

$session = New-Object WinSCP.Session
try {
    $session.Open($so)

    # Remove old assets/ to avoid stale hashed files
    if ($session.FileExists("/frai.tv/assets/")) {
        Write-Host "  Cleaning old /frai.tv/assets/..." -ForegroundColor Yellow
        $session.RemoveFiles("/frai.tv/assets/*").Check()
    }

    # Upload ALL dist files (synchronize)
    $transferOptions = New-Object WinSCP.TransferOptions
    $transferOptions.TransferMode = [WinSCP.TransferMode]::Binary

    # Upload index.html
    $session.PutFiles("$DistDir\index.html", $Remote, $false, $transferOptions).Check()
    Write-Host "  + index.html" -ForegroundColor Gray

    # Upload .htaccess
    if (Test-Path "$DistDir\.htaccess") {
        $session.PutFiles("$DistDir\.htaccess", $Remote, $false, $transferOptions).Check()
        Write-Host "  + .htaccess" -ForegroundColor Gray
    }

    # Upload robots.txt
    if (Test-Path "$DistDir\robots.txt") {
        $session.PutFiles("$DistDir\robots.txt", $Remote, $false, $transferOptions).Check()
        Write-Host "  + robots.txt" -ForegroundColor Gray
    }

    # Upload sitemap.xml
    if (Test-Path "$DistDir\sitemap.xml") {
        $session.PutFiles("$DistDir\sitemap.xml", $Remote, $false, $transferOptions).Check()
        Write-Host "  + sitemap.xml" -ForegroundColor Gray
    }

    # Upload favicon
    if (Test-Path "$DistDir\favicon.svg") {
        $session.PutFiles("$DistDir\favicon.svg", $Remote, $false, $transferOptions).Check()
        Write-Host "  + favicon.svg" -ForegroundColor Gray
    }

    # Upload manifest.json (PWA)
    if (Test-Path "$DistDir\manifest.json") {
        $session.PutFiles("$DistDir\manifest.json", $Remote, $false, $transferOptions).Check()
        Write-Host "  + manifest.json" -ForegroundColor Gray
    }

    # Upload og-image
    if (Test-Path "$DistDir\og-image.svg") {
        $session.PutFiles("$DistDir\og-image.svg", $Remote, $false, $transferOptions).Check()
        Write-Host "  + og-image.svg" -ForegroundColor Gray
    }

    # Upload icons/ (PWA icons)
    if (Test-Path "$DistDir\icons") {
        if (-not $session.FileExists("/frai.tv/icons/")) {
            $session.CreateDirectory("/frai.tv/icons/")
        }
        $result = $session.PutFiles("$DistDir\icons\*", "/frai.tv/icons/", $false, $transferOptions)
        $result.Check()
        Write-Host "  + icons/ ($($result.Transfers.Count) files)" -ForegroundColor Gray
    }

    # Upload assets/
    if (Test-Path "$DistDir\assets") {
        $result = $session.PutFiles("$DistDir\assets\*", "/frai.tv/assets/", $false, $transferOptions)
        $result.Check()
        Write-Host "  + assets/ ($($result.Transfers.Count) files)" -ForegroundColor Gray
    }

    # Upload watch/ (static SEO landing pages)
    if (Test-Path "$DistDir\watch") {
        if (-not $session.FileExists("/frai.tv/watch/")) {
            $session.CreateDirectory("/frai.tv/watch/")
        }
        $watchSync = $session.SynchronizeDirectories(
            [WinSCP.SynchronizationMode]::Remote,
            "$DistDir\watch",
            "/frai.tv/watch/",
            $false
        )
        $watchSync.Check()
        Write-Host "  + watch/ (synced)" -ForegroundColor Gray
    }

    # Upload pre-rendered static page directories (timeline, live, impressum, datenschutz)
    $staticDirs = @("timeline", "live", "impressum", "datenschutz")
    foreach ($dir in $staticDirs) {
        if (Test-Path "$DistDir\$dir") {
            if (-not $session.FileExists("/frai.tv/$dir/")) {
                $session.CreateDirectory("/frai.tv/$dir/")
            }
            $session.PutFiles("$DistDir\$dir\*", "/frai.tv/$dir/", $false, $transferOptions).Check()
            Write-Host "  + $dir/" -ForegroundColor Gray
        }
    }

    Write-Host "[OK] All files uploaded" -ForegroundColor Green

} catch {
    Write-Host "[ERROR] Upload failed: $_" -ForegroundColor Red
    exit 1
} finally {
    $session.Dispose()
}

# ── Verify ───────────────────────────────────────────────────
Write-Host "`n[3/3] Verifying..." -ForegroundColor Cyan
try {
    $r = Invoke-WebRequest -Uri "https://frai.tv" -UseBasicParsing -TimeoutSec 10
    $title = if ($r.Content -match '<title>([^<]+)</title>') { $Matches[1] } else { '?' }
    Write-Host "[OK] frai.tv responds (title: $title)" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Could not verify: $_" -ForegroundColor Yellow
}

try {
    $r2 = Invoke-WebRequest -Uri "https://frai.tv/robots.txt" -UseBasicParsing -TimeoutSec 10
    if ($r2.Content -match 'Sitemap') {
        Write-Host "[OK] robots.txt served correctly" -ForegroundColor Green
    } else {
        Write-Host "[WARN] robots.txt may be SPA-fallback" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[WARN] robots.txt check failed" -ForegroundColor Yellow
}

Write-Host "`n=========================================" -ForegroundColor Green
Write-Host "   frai.tv DEPLOYED!" -ForegroundColor Green
Write-Host "   https://frai.tv" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Green
