import spotipy
import string
import datetime

from spotipy.oauth2 import SpotifyClientCredentials
from difflib import SequenceMatcher
from typing import *

import config as CONFIG


spot = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(
        client_id=CONFIG.SPOT_CLIENT_ID,
        client_secret=CONFIG.SPOT_CLIENT_SECRET,
    )
)


class SpotifyHandler:
    @staticmethod
    def get_artist(artist_id: str) -> Tuple[str, str]:
        """`artist_id` : artist ID/URL/URI"""
        try:
            artist = spot.artist(artist_id)
            if artist["type"] != "artist":
                raise Exception
            return artist
        except Exception as e:
            print(f"UserError: {e}")

    @staticmethod
    def get_link(album: dict) -> str:
        """
        to get the link of an album received from spotipy
        >>> get_link(album)
        """
        return album["external_urls"]["spotify"]

    @staticmethod
    def _album_info(album: dict) -> dict:
        return {
            "id": album["id"],
            "name": album["name"],
            "type": album["type"],
            "album_group": album["album_group"],
            "album_type": album["album_type"],
            "release_date": album["release_date"],
            "artists": [
                {
                    "name": artist["name"],
                    "id": artist["id"],
                    "url": artist["external_urls"]["spotify"],
                }
                for artist in album["artists"]
            ],
            "urls": [
                album["external_urls"]["spotify"],
            ],
            "total_tracks": album["total_tracks"],
        }

    @staticmethod
    def _get_albums(
        artist: str, total: list = [], offset: int = 0, album_type: str = None
    ) -> list:
        """
        gets total albums of an artist (with no changes)
        >>> album_type='album,single,compilation,appears_on'
        >>> _get_albums('2iHrc69sZgyWFBAhLpS3oH')
        """
        albums = spot.artist_albums(
            artist, offset=offset, limit=50, album_type=album_type, country="AU"
        )
        total += albums["items"]
        if albums["next"]:
            total = SpotifyHandler._get_albums(
                artist=artist, total=total, offset=offset + 50
            )
        return total

    @staticmethod
    def get_albums(
        artist_id: str,
        show_first: int = 7,
        artist_name: str = None,
        album_type: str = None,
    ) -> dict:
        """
        use `show_first=None` to get all the albums\n
        use `artist_name` if you've already checked the artist and have the artist's name and id
        >>> get_albums('2iHrc69sZgyWFBAhLpS3oH')
        """
        if not artist_name:
            artist_obj = spot.artist(artist_id)
            artist_name, artist_id = artist_obj["name"], artist_obj["id"]
        albums = SpotifyHandler._get_albums(
            artist=artist_id,
            total=[],
            album_type=album_type,
        )
        albums.sort(
            key=lambda album: SpotifyHandler.str_to_time(album["release_date"]),
            reverse=True,
        )

        _albums = []
        for idx, album in enumerate(albums[:25]):
            if (
                album["album_group"] == "appears_on"
                and album["artists"][0]["name"] == "Various Artists"
            ):
                continue
            if idx == 0:
                _albums.append(SpotifyHandler._album_info(album))
            else:
                prev_album = albums[idx - 1]
                cond = abs(
                    SpotifyHandler.str_to_time(album["release_date"])
                    - SpotifyHandler.str_to_time(prev_album["release_date"])
                ) <= abs(datetime.timedelta(days=1).total_seconds())

                # check similarity in names
                # _similarity = SpotifyYR.similarity(album['name'], prev_album['name']) > 96
                name, prev_name, same_letters = "", "", True
                total_letters = list(
                    set(string.ascii_lowercase + string.ascii_uppercase + string.digits)
                )
                for letter in album["name"]:
                    if letter in total_letters:
                        name += letter.lower()
                for letter in prev_album["name"]:
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
                """cond &= album['name'] == prev_album['name']"""

                cond &= album["album_group"] == prev_album["album_group"]
                cond &= album["album_type"] == prev_album["album_type"]
                cond &= album["artists"] == prev_album["artists"]
                if cond:
                    _albums[-1]["urls"].append(SpotifyHandler.get_link(album))
                else:
                    _albums.append(SpotifyHandler._album_info(album))

        if show_first:
            _albums = _albums[:show_first]
        return {
            "name": artist_name,
            "albums": _albums,
        }

    @staticmethod
    def _track_info(track: dict) -> dict:
        return {
            "id": track["id"],
            "name": track["name"],
            "type": track["type"],
            "artists": [
                {
                    "name": artist["name"],
                    "id": artist["id"],
                    "url": artist["external_urls"]["spotify"],
                }
                for artist in track["artists"]
            ],
            "url": track["external_urls"]["spotify"],
        }

    @staticmethod
    def _get_tracks(album_id: str, total: list = [], offset: int = 0) -> list:
        albums = spot.album_tracks(album_id, limit=50, offset=offset, market="AU")
        total += albums["items"]
        if albums["next"]:
            total = SpotifyHandler._get_tracks(
                album_id=album_id, total=total, offset=offset + 50
            )
        return total

    @staticmethod
    def get_tracks(album_id: str):
        tracks = SpotifyHandler._get_tracks(album_id=album_id, total=[], offset=0)
        return [SpotifyHandler._track_info(track) for track in tracks]

    @staticmethod
    def similarity(a: str, b: str) -> float:
        """the percentage of similarity between a and b"""
        return SequenceMatcher(None, a, b).ratio() * 100

    @staticmethod
    def str_to_time(string: str) -> int:
        """
        returns total timestamp (even before 1970)
        >>> str_to_time('2018-19-26') in utc
        """
        _split = string.split("-")
        if len(_split) == 0:
            _split.append("0001")
        if len(_split) < 3:
            _split.append("01")
        if len(_split) < 3:
            _split.append("01")
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
            datetime.datetime(*_split, tzinfo=datetime.timezone.utc)
            - datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
        ).total_seconds()
