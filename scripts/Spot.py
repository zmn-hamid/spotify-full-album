import spotipy
import datetime
import string
from spotipy.oauth2 import SpotifyClientCredentials
from typing import *
from difflib import SequenceMatcher

import mein
from config import SPOT_CLIENT_ID, SPOT_CLIENT_SECRET


spot = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(
        client_id=SPOT_CLIENT_ID,
        client_secret=SPOT_CLIENT_SECRET,
    )
)


class SpotifyManager:
    @staticmethod
    def get_artist(artist_id: str) -> Tuple[str, str]:
        return spot.artist(artist_id)

    @staticmethod
    def get_link(album: dict) -> str:
        return album['external_urls']['spotify']

    @staticmethod
    def _album_info(album: dict) -> dict:
        return {
            'id': album['id'],
            'name': album['name'],
            'type': album['type'],
            'album_group': album['album_group'],
            'album_type': album['album_type'],
            'release_date': album['release_date'],
            'artists': [{
                'name': artist['name'],
                'id': artist['id'],
                'url': artist['external_urls']['spotify'],
            } for artist in album['artists']],
            'urls': [
                album['external_urls']['spotify'],
            ],
            'total_tracks': album['total_tracks'],
        }

    @staticmethod
    def _get_albums(artist: str,
                    total: list = [],
                    offset: int = 0,
                    album_type: str = None) -> list:
        albums = spot.artist_albums(artist, offset=offset, limit=50,
                                    album_type=album_type)  # album_type='album,single,compilation'
        total += albums['items']
        if albums['next']:
            total = SpotifyManager._get_albums(
                artist=artist,
                total=total,
                offset=offset+50
            )
        return total

    @staticmethod
    def get_albums(artist_id: str,
                   show_first: int = 7,
                   artist_name: str = None,
                   album_type: str = None) -> dict:
        if not artist_name:
            artist_obj = spot.artist(artist_id)
            artist_name, artist_id = artist_obj['name'], artist_obj['id']
        albums = SpotifyManager._get_albums(
            artist=artist_id,
            total=[],
            album_type=album_type,
        )
        albums.sort(
            key=lambda album: SpotifyManager.str_to_time(
                album['release_date']),
            reverse=True,
        )
        albums = list(filter(
            lambda item: len(item['available_markets']) >= 10,
            albums,
        ))

        _albums = []
        for idx, album in enumerate(albums[:25]):
            if album['album_group'] == 'appears_on' and album['artists'][0]['name'] == 'Various Artists':
                continue
            if idx == 0:
                _albums.append(SpotifyManager._album_info(album))
            else:
                prev_album = albums[idx-1]
                cond = abs(
                    SpotifyManager.str_to_time(
                        album['release_date']) - SpotifyManager.str_to_time(prev_album['release_date'])
                ) <= abs(datetime.timedelta(days=1).total_seconds())

                # check similarity in names
                # _similarity = SpotifyYR.similarity(album['name'], prev_album['name']) > 96
                name, prev_name, same_letters = '', '', True
                total_letters = list(
                    set(string.ascii_lowercase + string.ascii_uppercase + string.digits))
                for letter in album['name']:
                    if letter in total_letters:
                        name += letter.lower()
                for letter in prev_album['name']:
                    if letter in total_letters:
                        prev_name += letter.lower()
                if len(name) != len(prev_name):
                    same_letters = False
                else:
                    for idx, letter in enumerate(name):
                        if letter != prev_name[idx]:
                            same_letters = False
                            break
                # cond &= _similarity & same_letters
                cond &= same_letters
                '''cond &= album['name'] == prev_album['name']'''

                cond &= album['album_group'] == prev_album['album_group']
                cond &= album['album_type'] == prev_album['album_type']
                cond &= album['artists'] == prev_album['artists']
                if cond:
                    _albums[-1]['urls'].append(SpotifyManager.get_link(album))
                    _albums[-1]['url'] = SpotifyManager.get_link(album)
                else:
                    _albums.append(SpotifyManager._album_info(album))

        if show_first:
            _albums = _albums[:show_first]
        return {
            'name': artist_name,
            'albums': _albums,
        }

    @staticmethod
    def _track_info(track: dict) -> dict:
        return {
            'id': track['id'],
            'name': track['name'],
            'type': track['type'],
            'artists': [{
                'name': artist['name'],
                'id': artist['id'],
                'url': artist['external_urls']['spotify'],
            } for artist in track['artists']],
            'url': track['external_urls']['spotify'],
        }

    @staticmethod
    def _get_tracks(album_id: str,
                    total: list = [],
                    offset: int = 0) -> list:
        albums = spot.album_tracks(album_id, limit=50, offset=offset)
        total += albums['items']
        if albums['next']:
            total = SpotifyManager._get_tracks(
                album_id=album_id,
                total=total,
                offset=offset+50
            )
        return total

    @staticmethod
    def get_tracks(album_id: str):
        tracks = SpotifyManager._get_tracks(
            album_id=album_id, total=[], offset=0)
        return [SpotifyManager._track_info(track) for track in tracks]

    @staticmethod
    def similarity(a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()*100

    @staticmethod
    def str_to_time(string: str) -> int:
        _split = string.split('-')
        if len(_split) == 0:
            _split.append('0001')
        if len(_split) < 3:
            _split.append('01')
        if len(_split) < 3:
            _split.append('01')
        _split = list(map(int, _split))

        try:
            datetime.datetime(_split[0], 1, 1)
        except:
            _split[0] = 1
        try:
            datetime.datetime(1, _split[1], 1)
        except:
            _split[1] = 1
        try:
            datetime.datetime(1, 1, _split[2])
        except:
            _split[2] = 1

        return (
            datetime.datetime(
                *_split, tzinfo=datetime.timezone.utc
            ) - datetime.datetime(
                1970, 1, 1, tzinfo=datetime.timezone.utc
            )
        ).total_seconds()


if __name__ == '__main__':
    artist_url = 'https://open.spotify.com/artist/1hLiboQ98IQWhpKeP9vRFw?si=d0d6785d19b5423b'  # boygenius
    artist_url = 'https://open.spotify.com/artist/6S3Z6Me30mtdm526H17v8k?si=4gmhl2Z9T2mXq7wpeDG7ew'  # jockstrap
    artist_url = 'https://open.spotify.com/artist/7mRVAzlt1fAAR9Cut6Rq8c?si=28f9e80606d24d7a'  # dave grohl
    # albums = SpotifyManager.get_albums(artist_url, None)[::-1]
    albums = SpotifyManager.get_tracks('7M6NyPARixmFv74BbgUFFg')
    mein.dumps(albums, 'out')
