"""Quick check of diverged videos in DB."""
import sqlite3, json

db = sqlite3.connect('tools/channel_manager/channel_manager.db')
db.row_factory = sqlite3.Row

rows = db.execute('''
    SELECT v.id, v.title, v.privacy_status, vt.status, vt.divergence_details
    FROM video_targets vt
    JOIN videos v ON v.id = vt.video_id
    WHERE vt.status = 'diverged'
    ORDER BY v.title
''').fetchall()

print(f"=== {len(rows)} DIVERGED VIDEOS ===\n")
for r in rows:
    vid = r['id']
    title = r['title'][:65]
    priv = r['privacy_status']
    details = r['divergence_details'] or ''
    print(f"  {vid} [{priv:7s}]")
    print(f"    {title}")
    if details:
        print(f"    Details: {details[:150]}")
    print()

# Also check Soundies playlist status
print("\n=== SOUNDIES PLAYLIST CHECK ===\n")
soundies = db.execute('''
    SELECT v.id, v.title
    FROM videos v
    WHERE v.privacy_status = 'public'
    AND (LOWER(v.title) LIKE '%soundie%' OR LOWER(v.tags) LIKE '%soundie%')
    ORDER BY v.title
''').fetchall()
print(f"Total Soundie videos: {len(soundies)}")
for s in soundies:
    print(f"  {s['id']} | {s['title'][:60]}")

# Get all playlists
playlists = db.execute("SELECT playlist_id, title, video_count FROM playlists ORDER BY title").fetchall()
print("\nPlaylists with 'Soundie':")
for p in playlists:
    if 'soundie' in p['title'].lower() or 'soundies' in p['title'].lower():
        print(f"  {p['playlist_id']} | {p['title']} | {p['video_count']} videos")

db.close()
