from flask import Flask, render_template, request
app = Flask(__name__)

from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json


load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


def get_token():
    """Get Spotify API Token."""
    auth_string = f"{client_id}:{client_secret}"
    auth_base64 = base64.b64encode(auth_string.encode()).decode()

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content_Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data).json()
    return result["access_token"]


def get_auth_header(token):
    """Generate authorization header."""
    return {"Authorization": f"Bearer {token}"}


def search_for_artist(token, artist_name):
    """Search for an artist by name."""
    url = f"https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit=1"
    result = get(url, headers=get_auth_header(token)).json()
    artists = result.get("artists", {}).get("items", [])

    if not artists:
        print("No artist found, please try again.")
        return None

    return artists[0]


def get_songs_by_artist(token, artist_id):
    """Get top tracks of an artist."""
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    result = get(url, headers=get_auth_header(token)).json()
    return result.get("tracks", [])


def get_albums_by_artist(token, artist_id):
    """Get albums by an artist."""
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    result = get(url, headers=get_auth_header(token)).json()
    return result.get("items", [])


def get_related_artists(token, artist_id):
    """Get artists related to the given artist."""
    url = f"https://api.spotify.com/v1/artists/{artist_id}/related-artists"
    result = get(url, headers=get_auth_header(token)).json()
    return result.get("artists", [])

@app.route('/', methods=['GET', 'POST'])
def index():
    artist_info = None
    if request.method == 'POST':
        artist_name = request.form['artist_name']
        token = get_token()
        artist = search_for_artist(token, artist_name)
        if artist:
            artist_info = {
                'name': artist['name'],
                'genres': ', '.join(artist.get('genres', [])),
                'popularity': artist.get('popularity', 'N/A'),
                'followers': artist['followers']['total'],
                'tracks': get_songs_by_artist(token, artist["id"]),
                'albums': get_albums_by_artist(token, artist["id"]),
                'related_artists': get_related_artists(token, artist["id"])
            }
    return render_template('index.html', artist_info=artist_info)

if __name__ == '__main__':
    app.run(debug=True)
