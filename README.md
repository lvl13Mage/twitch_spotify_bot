TODO

Quick and dirty

Requirements:
Python 3.9+ from python https://www.python.org/
Windows -> download: https://visualstudio.microsoft.com/de/downloads/ get C++ Desktop package
Twitch Developer Bot Credentials (client_id + client_secret) -> https://dev.twitch.tv/
Spotify Developer Bot Credentials (client_id + client_secret) -> https://developer.spotify.com/

Install:
1. Create Spotify APP with callback http://localhost:8888/callback
2. Create Twitch APP with callback http://localhost:4000 and https://localhost
3. Unzip dir
4. Fill in credentials to config/config.json (important are twitch_client_id, twitch_client_secret, spotify_client_id, spotify_client_secret)
5. Run setupBot.bat (installs python dependencies)
6. Run startBot.bat (starts the bot)

The bot will open oauth for twitch and spotify and ask for permissions. 

If you have trouble creating the apps with http:// , try creating multiple callbacks with https:// to meet their requirements. 
This app uses the http one for local use only tho. 
