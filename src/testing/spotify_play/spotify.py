import os

from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

from dotenv import load_dotenv
load_dotenv()

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

client_credentials_manager = SpotifyClientCredentials(
    client_id=client_id, client_secret=client_secret)
sp = Spotify(client_credentials_manager=client_credentials_manager)

result = sp.search(q='Yung Beef', limit=1, type='artist')
print(result)

artist_id = result['artists']['items'][0]['id']
albums = sp.artist_albums(artist_id=artist_id, album_type='album')

print()

for album in albums['items']:
    print(album['name'])
