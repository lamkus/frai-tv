from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/youtube'])
if creds.expired:
    creds.refresh(Request())
yt = build('youtube', 'v3', credentials=creds)

# Rebind WHoKI4Fk8jI to "permastream" (key ending 3be3)
result = yt.liveBroadcasts().bind(
    id='WHoKI4Fk8jI',
    part='id,snippet,contentDetails,status',
    streamId='VFv6Egpl0LDvigpFbQXNeQ1771887015419315'
).execute()
status = result['status']['lifeCycleStatus']
print(f'Rebound to permastream: {status}')
