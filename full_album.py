import os

from scripts.Spot import SpotifyManager
from scripts.TextFormatter import Style, BLOCK

LINE = Style.header('|')


def print_album(album_obj):
    print(LINE, '%s | %s | %s | %s' % (Style.album(
        album_obj['name']),
        album_obj['album_group'],
        album_obj['release_date'],
        album_obj['url']))


def print_new_track(track_name):
    print(LINE+'    '+Style.new_track(track_name))


def print_old_track(track_name):
    print(LINE+'    '+Style.old_track(track_name))


def clear_terminal():
    os.system('cls||clear')


def main(artist_url: str):
    artist_obj = SpotifyManager.get_artist(artist_url)
    print(Style.header(BLOCK+BLOCK+BLOCK+' '+artist_obj['name']))

    artist_id = artist_obj['id']
    artist_albums = SpotifyManager.get_albums(artist_id, None)['albums'][::-1]

    # a record of all the new tracks
    total_tracks = []

    print()
    print()

    # process albums
    print(Style.header('--- ALBUMS ---'))
    for album in artist_albums:
        if album['album_group'].lower() == 'album':
            print_album(album)
            tracks = SpotifyManager.get_tracks(album_id=album['id'])
            for track in tracks:
                track_name = track['name']
                if track_name in total_tracks:
                    print_old_track(track_name)
                else:
                    total_tracks.append(track_name)
                    print_new_track(track_name)
    print(Style.header('---------'))

    print()
    print()

    # process others
    print(Style.header('--- OTHERS ---'))
    for album in artist_albums:
        if album['album_group'].lower() not in ['album', 'appears_on']:
            print_album(album)
            tracks = SpotifyManager.get_tracks(album_id=album['id'])
            for track in tracks:
                track_name = track['name']
                if track_name in total_tracks:
                    print_old_track(track_name)
                else:
                    total_tracks.append(track_name)
                    print_new_track(track_name)
    print(Style.header('---------'))

    print()
    print()

    # process appears_on
    print(Style.header('--- APPEARS ON ---'))
    for album in artist_albums:
        if album['album_group'].lower() == 'appears_on':
            print_album(album)
            tracks = SpotifyManager.get_tracks(album_id=album['id'])
            for track in tracks:
                # check if the main artist is involved
                for track_artist in track['artists']:
                    if track_artist['id'] == artist_id:
                        track_name = track['name']
                        if track_name in total_tracks:
                            print_old_track(track_name)
                        else:
                            total_tracks.append(track_name)
                            print_new_track(track_name)
                        break
    print(Style.header('---------'))

    print()
    print()
    print(Style.header(BLOCK+BLOCK+BLOCK+' finished'))


if __name__ == '__main__':
    try:
        # artist_url = 'https://open.spotify.com/artist/7mRVAzlt1fAAR9Cut6Rq8c?si=28f9e80606d24d7a'  # dave grohl
        print(Style.intro('''

        This app is to get all the releases of your favorite musician/band/... from spotify.
        
        If a track exists in a studio album or previous releases, it'll be shown with yellow
        And any other track (which are supposed to be unique) are in green.
        
        Copy the URL of your artist from spotify and paste it bellow
        
        '''))
        artist_url = input(Style.question("Enter URL: "))
        if artist_url:
            clear_terminal()
            main(artist_url)
        else:
            print('no artist entered... ', end='')
            raise KeyboardInterrupt
    except KeyboardInterrupt:
        print('exitting...')
