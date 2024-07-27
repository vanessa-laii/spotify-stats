import os
from flask import Flask, redirect, request, session, url_for, render_template, flash
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

# Load Spotify API credentials from environment variables
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
redirect_uri = os.getenv('REDIRECT_URI')
scope = 'user-read-private, playlist-read-private'

# Set up Spotify OAuth
cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
)

sp = Spotify(auth_manager=sp_oauth)

@app.route('/')
def home():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for('profile'))

@app.route('/callback')
def callback():
    try:
        sp_oauth.get_access_token(request.args['code'])
    except Exception as e:
        flash(f"Error: {e}", 'danger')
        return redirect(url_for('home'))
    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    user = sp.current_user()
    return render_template('profile.html', user=user)

@app.route('/playlists')
def get_playlists():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    playlists = sp.current_user_playlists()
    return render_template('playlists.html', playlists=playlists['items'])

@app.route('/playlist/<playlist_id>')
def get_playlist_tracks(playlist_id):
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    tracks = sp.playlist_tracks(playlist_id)
    return render_template('tracks.html', tracks=tracks['items'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)