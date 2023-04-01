from scripts.Spot import SpotifyManager


def main(artist_url: str):
    artist_obj = SpotifyManager.get_artist(artist_url)
    artist_id = artist_obj['id']
    
    artist_albums = SpotifyManager.get_albums(artist_id, None)['albums'][::-1]

    # a record of all the new tracks
    total_tracks = []
    
    # process albums
    print('++ albums ++')
    for album in artist_albums:
        if album['album_group'].lower() == 'album':
            print('+ %s' %(album['name']))
            tracks = SpotifyManager.get_tracks(album_id=album['id'])
            for track in tracks:
                track_name = track['name']
                if track_name in total_tracks:
                    print('  - [OLD] %s' %track_name)
                else:
                    total_tracks.append(track_name)
                    print('  - [NEW] %s' %track_name)
    
    print()
    print()

    # process else
    print('++ others ++')
    for album in artist_albums:
        if album['album_group'].lower() not in ['album', 'appears_on']:
            print('+ %s' %(album['name']))
            tracks = SpotifyManager.get_tracks(album_id=album['id'])
            for track in tracks:
                track_name = track['name']
                if track_name in total_tracks:
                    print('  - [OLD] %s' %track_name)
                else:
                    total_tracks.append(track_name)
                    print('  - [NEW] %s' %track_name)
    
    
    print()
    print()

    # process appears_on
    print('++ appears on ++')
    for album in artist_albums:
        if album['album_group'].lower() == 'appears_on':
            print('+ %s' %(album['name']))
            tracks = SpotifyManager.get_tracks(album_id=album['id'])
            for track in tracks:
                # check if the main artist is involved
                for track_artist in track['artists']:
                    if track_artist['id'] == artist_id:
                        track_name = track['name']
                        if track_name in total_tracks:
                            print('  - [OLD] %s' %track_name)
                        else:
                            total_tracks.append(track_name)
                            print('  - [NEW] %s' %track_name)
                        break


if __name__ == '__main__':
    artist_url = 'https://open.spotify.com/artist/7mRVAzlt1fAAR9Cut6Rq8c?si=28f9e80606d24d7a' # dave grohl
    main(artist_url)

