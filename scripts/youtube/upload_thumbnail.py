"""
upload_thumbnail.py - Upload custom thumbnail to YouTube broadcast
=================================================================
Uploads a local image file as custom thumbnail for a YouTube video/broadcast.

Usage:
    python scripts/youtube/upload_thumbnail.py                          # Auto-detect live broadcast + branded thumb
    python scripts/youtube/upload_thumbnail.py --video-id lm4EcKHQ45o  # Specific video
    python scripts/youtube/upload_thumbnail.py --image path/to/thumb.jpg --video-id VIDEO_ID

Requirements: Channel must be phone-verified for custom thumbnails.
"""
import os, sys, json, argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')
CLIENT_SECRET = os.path.join(BASE_DIR, 'config', 'client_secret.json')
BROADCAST_STATE = os.path.join(BASE_DIR, 'config', 'broadcast_state.json')
DEFAULT_THUMBNAIL = os.path.join(BASE_DIR, 'assets', 'wochenschau', 'thumbnails', 'stream_thumbnail_branded.jpg')


def get_youtube_service():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)


def get_live_broadcast_id():
    """Get current live broadcast ID from state file."""
    if os.path.exists(BROADCAST_STATE):
        with open(BROADCAST_STATE) as f:
            state = json.load(f)
        bid = state.get('broadcast_id')
        if bid:
            return bid
    return None


def upload_thumbnail(yt, video_id, image_path):
    """Upload custom thumbnail to a YouTube video."""
    from googleapiclient.http import MediaFileUpload

    if not os.path.exists(image_path):
        print(f'[ERROR] Image not found: {image_path}')
        return False

    size = os.path.getsize(image_path)
    if size > 2 * 1024 * 1024:
        print(f'[ERROR] Image too large: {size:,} bytes (max 2MB)')
        return False

    ext = os.path.splitext(image_path)[1].lower()
    mime_map = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.gif': 'image/gif'}
    mime = mime_map.get(ext, 'image/jpeg')

    print(f'[THUMBNAIL] Uploading to video {video_id}...')
    print(f'  File: {image_path}')
    print(f'  Size: {size:,} bytes')
    print(f'  MIME: {mime}')

    try:
        media = MediaFileUpload(image_path, mimetype=mime, resumable=True)
        response = yt.thumbnails().set(
            videoId=video_id,
            media_body=media
        ).execute()

        print(f'[SUCCESS] Thumbnail uploaded!')
        items = response.get('items', [])
        if items:
            for key, thumb in items[0].items():
                if isinstance(thumb, dict) and 'url' in thumb:
                    print(f'  {key}: {thumb["url"][:80]}')
        return True

    except Exception as e:
        error_str = str(e)
        if 'forbidden' in error_str.lower():
            print(f'[ERROR] Forbidden - channel may not be verified for custom thumbnails')
        elif 'notFound' in error_str.lower():
            print(f'[ERROR] Video {video_id} not found')
        else:
            print(f'[ERROR] {e}')
        return False


def main():
    parser = argparse.ArgumentParser(description='Upload custom thumbnail to YouTube')
    parser.add_argument('--video-id', type=str, help='YouTube video/broadcast ID')
    parser.add_argument('--image', type=str, help='Path to thumbnail image (max 2MB, 1280x720 recommended)')
    args = parser.parse_args()

    # Resolve video ID
    video_id = args.video_id
    if not video_id:
        video_id = get_live_broadcast_id()
        if video_id:
            print(f'[AUTO] Using live broadcast: {video_id}')
        else:
            print('[ERROR] No video ID specified and no live broadcast found')
            print('  Use: --video-id YOUR_VIDEO_ID')
            sys.exit(1)

    # Resolve image path
    image_path = args.image or DEFAULT_THUMBNAIL
    if not os.path.isabs(image_path):
        image_path = os.path.join(BASE_DIR, image_path)

    print('=' * 60)
    print('  THUMBNAIL UPLOAD')
    print('=' * 60)

    yt = get_youtube_service()
    success = upload_thumbnail(yt, video_id, image_path)

    if success:
        print('\n[DONE] Custom thumbnail is now live!')
        print(f'  Video: https://youtube.com/watch?v={video_id}')
    else:
        print('\n[FAILED] Thumbnail upload failed.')
        sys.exit(1)


if __name__ == '__main__':
    main()
