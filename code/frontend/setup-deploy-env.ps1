# ============================================================
# FRAI.TV - Deployment Setup (EINMALIG AUSFÜHREN)
# ============================================================
# Diese Datei setzt alle nötigen Umgebungsvariablen für Deployment.
# Führe diese Datei VOR deploy.ps1 aus!
#
# NUTZUNG:
#   . .\setup-deploy-env.ps1   (Punkt-Space wichtig!)
#   .\deploy.ps1
# ============================================================

# Strato SFTP Zugangsdaten
$env:STRATO_SFTP_HOST = "510738084.ssh.w1.strato.hosting"
$env:STRATO_SFTP_USER = "stu897064236"
$env:STRATO_SFTP_REMOTE_PATH = "/FRai.TV/"

Write-Host "Strato-Credentials gesetzt:" -ForegroundColor Green
Write-Host "  Host: $env:STRATO_SFTP_HOST" -ForegroundColor Cyan
Write-Host "  User: $env:STRATO_SFTP_USER" -ForegroundColor Cyan
Write-Host "  Path: $env:STRATO_SFTP_REMOTE_PATH" -ForegroundColor Cyan
Write-Host ""
Write-Host "Jetzt ausfuehren: .\deploy.ps1" -ForegroundColor Yellow
