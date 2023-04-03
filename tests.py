import unittest

from scripts.SpotifyHandler import SpotifyHandler


class FullAlbumTests(unittest.TestCase):
    def test_wrong_artist_id_fails(self):
        self.assertFalse(SpotifyHandler().get_artist(
            'wrong artist ID/URL/URI'))


if __name__ == '__main__':
    unittest.main()
