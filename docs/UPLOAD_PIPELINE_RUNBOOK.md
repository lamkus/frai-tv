# Upload Pipeline Runbook

This document describes how to install, run, and operate the Local → YouTube → FRai.TV upload pipeline (Manual-First). It includes setup, service options, and troubleshooting.

## Prerequisites
- Python 3.8+
- ffmpeg/ffprobe (optional, recommended for real duration/resolution): https://ffmpeg.org/download.html
- A YouTube OAuth authorized user JSON (see `docs/YOUTUBE_OAUTH_ONECLICK_DEPLOY.md`)
- FRai.TV API key with permission to `/api/videos/sync`

## Install Python deps
```bash
pip install -r code/backend/scripts/python-requirements.txt
```

## Configuration
- Copy `config/upload_pipeline_config.json.sample` to `config/upload_pipeline_config.json` or edit `config/upload_pipeline_config.json` directly.
- Set `watch_directories`, `folder_playlist_mapping`, `fraitv_api_key`, and `youtube_credentials_path`.
- `retry.max_retries` and `retry.base_delay_seconds` control retry/backoff behaviour.

## Run once
```bash
python code/backend/scripts/auto_upload_pipeline.py config/upload_pipeline_config.json --once
```

## Run as a long-running service

### Docker (recommended for Checkdomain / Render)
- Fill `config/.env.auto_upload` (copy from `config/.env.auto_upload.sample`) with your secrets and paths.
- Build and push image (example):
```bash
./code/backend/scripts/build_push_worker.sh frai/autoupload:latest
# then push: docker push frai/autoupload:latest
```
- Start with docker-compose locally:
```bash
docker-compose -f docker-compose.worker.yml up --build -d
```
- Health endpoint: `http://<host>:8081/health` returns 200 if the worker is running.

### Windows (recommended if not using Docker): Scheduled Task
- Edit `code/backend/scripts/install_windows_scheduled_task.ps1` parameters and run it in PowerShell as Admin:
```powershell
.\code\backend\scripts\install_windows_scheduled_task.ps1 -PythonExe "C:\Python39\python.exe" -ScriptPath "D:\remaike.TV\code\backend\scripts\auto_upload_pipeline.py" -ConfigPath "D:\remaike.TV\config\upload_pipeline_config.json"
```
- This creates a scheduled task that runs at startup and restarts on failure.

### Alternative: PM2 (Node + PM2 installed)
- From `code/backend/scripts`:
```bash
pm2 start pm2_ecosystem.config.js
pm2 save
```

## Logs
- Logs are written to `logs/auto_upload.log` with daily rotation (14 backups).

## Deploying to Checkdomain
- If Checkdomain supports Docker, push the built image to your registry and point Checkdomain to the image tag.
- Use the `HEALTH_PORT` / `HEALTH_URL` (default `/health`) for platform health checks.
- Mount your watch directories into `/watch` in the container and update `WATCH_DIRECTORIES` in env to `/watch`.

## Monitoring & Errors
- Uploads and syncs have built-in retry/backoff; inspect `logs/auto_upload.log` for failures.
- Common issues:
  - OAuth expired/invalid credentials: re-run OAuth flow and place authorized file at `youtube_credentials_path`.
  - FRai.TV 401/403: verify `fraitv_api_key` has permission.
  - ffprobe missing: install ffmpeg and ensure `ffprobe` is available on PATH.

## Adding metadata overrides
- Place a JSON file next to the video (same name, `.json`) with keys `title`, `description`, `tags` to override auto-generated metadata.

## Next steps / Phase 2
- Add central Node adapter for logging/metrics and queue (T-154)
- Add optional virus scan integration
- Add test fixtures and CI job to validate upload flows

If you want, I can also add a Windows Event Log integration or a Health endpoint for a small wrapper service.