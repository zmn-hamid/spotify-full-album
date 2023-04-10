# Spotify Full Album Finder

Find and spot every release of your chosen artist in spotify.

#### Features

- Showing the repetitive tracks in a strikethrough yellow and other first-appeared tracks in green
- Fist, albums are analyzed, then singles/EPs/etc, then 'appears on's. So if the song is in a album, it shows it in green only for the album.

## Getting Started

#### Prerequisites

You need to install python 3 and add it to your systems path.
My python version: 3.11.2

### Installation

1. Open terminal in the root directory and install requirement with this command:
   ```
   pip install -r requirements.txt
   ```
2. Make a `config.py` file in the root directory, and put this text inside it:
   ```
   SPOT_CLIENT_ID = 'Your Client ID'
   SPOT_CLIENT_SECRET = 'Your Client Secret'
   ```
   to find your client ID and secret, make an app in [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and find them in the settings of the app.

#### Usage

Once you're in the root directory, simply run the app using `python full_album.py`.

#### Demo

https://user-images.githubusercontent.com/129656474/229351305-b39e9abc-d045-453a-a54c-18670cef3fa9.mp4

## License

MIT License

This project is free and open-source. You can use, modify, and distribute it without any restrictions.

## Contact

If you have any questions or feedback about this project, feel free to get in touch with me:

- Email: zmn-hamid@proton.me
- [Telegram](https://t.me/hamid1780)
- [GitHub Issues](https://github.com/zmn-hamid/spotify-full-album/issues)
