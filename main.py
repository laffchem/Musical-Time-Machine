import spotipy
from spotipy.oauth2 import SpotifyOAuth
from art import logo
import os
from bs4 import BeautifulSoup
import requests
import datetime as dt

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
REDIRECT_URI = os.environ.get('REDIRECT')

print(logo)

print(
  "Welcome to the Musical Time Machine, this creates a playlist from the Billboard Top 100 Playlist from a given date!"
)

year = None

while year == None:
  try:
    time_travel = input(
      "What year would you like to travel to? Type this as YYYY-MM-DD:\n")
    time_travel_date = dt.datetime.strptime(time_travel, '%Y-%m-%d')
  except ValueError as err:
    print(f"Incorrect input: ", err)
  else:
    year = dt.datetime.strftime(time_travel_date, "%Y")
    print(year)

response = requests.get(
  f"https://www.billboard.com/charts/hot-100/{time_travel}")
response.raise_for_status()

songs = response.text

soup = BeautifulSoup(songs, 'html.parser')

song_names_spans = soup.find_all(
  "h3",
  class_=
  "c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 u-max-width-230@tablet-only"
)

song_list = [
  song.getText().replace('\n', '').replace('\t', '')
  for song in song_names_spans
]

# print(song_list)

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
  client_id=CLIENT_ID,
  client_secret=CLIENT_SECRET,
  redirect_uri=REDIRECT_URI,
  scope="playlist-modify-public",
  show_dialog=True,
  cache_path="token.txt",
))
user_id = sp.current_user()["id"]

# Search for songs that were scraped, then append their spotify uris to a list.

song_uris = []
for song in song_list:
  result = sp.search(q=f"track:{song} year:{year}", type='track')
  print(result)
  try:
    uri = result['tracks']['items'][0]['uri']
    song_uris.append(uri)
  except IndexError:
    print(f"{song} doesn't exist in Spotify. Skipped.")

#Create the playlist
playlist = sp.user_playlist_create(
  user=user_id,
  name=f"Billboard Top 100 from {time_travel}",
  public=True,
  collaborative=False)
playlist_id = playlist['id']

sp.playlist_add_items(playlist_id=playlist_id, items=song_uris)
