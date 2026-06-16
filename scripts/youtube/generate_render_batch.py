"""Generate a standalone batch file with all FFmpeg render commands.

This removes Python from the render loop completely.
The batch file runs FFmpeg directly for each episode — no Python process to kill.
"""

import json
import os
import sys
import subprocess
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

# Load config
with open('config/wochenschautv_config.json', encoding='utf-8') as f:
    config = json.load(f)

# Use the existing load_episodes and scan functions from wochenschautv
from scripts.youtube.wochenschautv import (
    load_episodes, scan_video_files, build_timeline_filters, _probe_duration
)

episodes = load_episodes()
print(f"Loaded {len(episodes)} episodes from databases")

# Scan for video files
matched, unmatched = scan_video_files(config, episodes)
print(f"Matched {matched} episodes with video files")

# Filter to those with files
available = [ep for ep in episodes if ep.get('file_path')]
available.sort(key=lambda x: x['number'])

# Resolution from config
res = config['ffmpeg'].get('resolution', '1920x1080')
out_w, out_h = [int(x) for x in res.split('x')]
if out_h >= 2160:
    bitrate, maxrate, bufsize = '20000k', '25000k', '40000k'
else:
    bitrate, maxrate, bufsize = '8000k', '10000k', '16000k'

output_dir = os.path.join(ROOT, 'watch', 'wochenschau_rendered')
os.makedirs(output_dir, exist_ok=True)

# Generate batch file
batch_lines = [
    '@echo off',
    'setlocal enabledelayedexpansion',
    f'cd /d {ROOT}',
    f'echo ==========================================',
    f'echo WochenschauTV Batch Render @ {res} {bitrate}',
    f'echo Episodes: {len(available)}',
    f'echo Started: %DATE% %TIME%',
    f'echo ==========================================',
    '',
]

for i, ep in enumerate(available):
    out_path = os.path.join(output_dir, f"WochenschauTV_Nr{ep['number']:03d}.mp4")
    log_path = os.path.join(ROOT, 'logs', f"ffmpeg_nr{ep['number']:03d}.log")
    
    # Set up next episode
    if i + 1 < len(available):
        ep['_next_episode'] = available[i + 1]
    else:
        ep['_next_episode'] = available[0]
    
    # Probe duration
    try:
        ep['_duration'] = _probe_duration(ep['file_path'])
    except Exception:
        ep['_duration'] = 0
    
    ep['_index'] = i + 1
    ep['_total'] = len(available)
    
    # Build filters
    filters = []
    filters.append(f"scale={out_w}:{out_h}:force_original_aspect_ratio=decrease")
    filters.append(f"pad={out_w}:{out_h}:(ow-iw)/2:(oh-ih)/2:black")
    filters.append(f"fps={config['ffmpeg']['fps']}")
    filters.extend(build_timeline_filters(ep, config))
    
    filter_str = ','.join(filters)
    
    # Build FFmpeg command (uses wstv_render.exe = renamed ffmpeg, immune to Stop-Process -Name ffmpeg)
    cmd_parts = [
        'wstv_render', '-y',
        '-threads', '0',
        '-i', f'"{ep["file_path"]}"',
        '-vf', f'"{filter_str}"',
        '-c:v', 'h264_nvenc',
        '-preset', 'p5',
        '-b:v', bitrate,
        '-maxrate', maxrate,
        '-bufsize', bufsize,
        '-pix_fmt', 'yuv420p',
        '-g', '50',
        '-bf', '2',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-ar', '44100',
        '-movflags', '+faststart',
        '-async', '1',
        f'"{out_path}"',
    ]
    
    ffmpeg_cmd = ' '.join(cmd_parts)
    
    batch_lines.append(f'echo.')
    batch_lines.append(f'echo [{i+1}/{len(available)}] Nr.{ep["number"]} - {ep.get("event_en", "Unknown")}')
    batch_lines.append(f'echo Rendering @ {res} {bitrate}...')
    
    # Skip if already exists and is large enough
    batch_lines.append(f'if exist "{out_path}" (')
    batch_lines.append(f'  for %%A in ("{out_path}") do if %%~zA GTR 50000000 (')
    batch_lines.append(f'    echo   SKIP: Already rendered ^(%%~zA bytes^)')
    batch_lines.append(f'    goto :skip_{ep["number"]}')
    batch_lines.append(f'  )')
    batch_lines.append(f')')
    
    # Delete any partial file
    batch_lines.append(f'if exist "{out_path}" del /f "{out_path}"')
    
    # Run FFmpeg with stderr to log file
    batch_lines.append(f'{ffmpeg_cmd} 2>"{log_path}"')
    batch_lines.append(f'if errorlevel 1 (')
    batch_lines.append(f'  echo   FAILED! Check {log_path}')
    batch_lines.append(f'  if exist "{out_path}" del /f "{out_path}"')
    batch_lines.append(f') else (')
    batch_lines.append(f'  echo   OK!')
    batch_lines.append(f')')
    batch_lines.append(f':skip_{ep["number"]}')
    batch_lines.append('')

batch_lines.append('echo.')
batch_lines.append('echo ==========================================')
batch_lines.append('echo Render complete at %DATE% %TIME%')
batch_lines.append('echo ==========================================')
batch_lines.append('pause')

# Write batch file
batch_path = os.path.join(ROOT, 'render_all.bat')
with open(batch_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(batch_lines))

print(f"\nGenerated: {batch_path}")
print(f"Resolution: {res}")
print(f"Bitrate: {bitrate}")
print(f"Episodes: {len(available)}")
print(f"\nTo render, run in a NEW cmd.exe window:")
print(f"  {batch_path}")
