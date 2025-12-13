## Frontend local development notes (D:)

If you want a local-only development copy on D: use this folder:
D:\remaike.TV (recommended)

Why? Native builds (esbuild, vite) may fail when the project is on a network-mapped drive (K:) due to native binary spawning / permission/locking issues. Keep the active development copy on a local volume.

Quick setup (PowerShell):

New-Item -ItemType Directory -Path "D:\remaike.TV" -Force
robocopy "C:\repos\remAIke.TV" "D:\remaike.TV" /E /XD node_modules .git /MT:8

# Frontend dev
cd D:\remaike.TV\code\frontend
npm install
npm run dev

# Production build
npm run build

# Cleanup if needed
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue
npm cache clean --force

# Notes
- We recommend working from a local drive. Keep backups on network or cloud.
