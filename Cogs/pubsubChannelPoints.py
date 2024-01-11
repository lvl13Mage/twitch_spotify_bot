import os
from twitchio.ext import commands, pubsub
from twitchio import CustomRewardRedemption
import requests
import asyncio
import json
import urllib.parse
import time
import simpleaudio as sa
from pprint import pprint
from Spotify.spotifyClient import SpotifyClient
from JsonPersistence.jsonSongerequestStorageHandler import JsonSongRequestStorageHandler

class PubSubChannelPoints(commands.Cog):

    def __init__(self, bot: commands.Bot, config):
        self.bot = bot 
        self.bot.pubsub = pubsub.PubSubPool(bot)
        self.user_oauth_token = config["twitch_access_token"]
        self.user_channel_id = int(config["client_id"])
        self.channel = config["channel"]
        self.config = config

    @commands.Cog.event()
    async def event_ready(self):
        topics = [
            pubsub.channel_points(self.user_oauth_token)[self.user_channel_id],
        ]
        await self.bot.pubsub.subscribe_topics(topics)

    @commands.Cog.event()
    async def event_pubsub_channel_points(self, event: pubsub.PubSubChannelPointsMessage):
        message = f"{event.user.name} used channel points:  '{event.reward.title}' for {str(event.reward.cost)} points."
        print(message)
  
        channel = self.bot.get_channel(self.channel)

        rewardName = event.reward.title
        spotify = SpotifyClient(self.config)

        match rewardName:
            case "Song Request":
                songerequestStorageHandler = JsonSongRequestStorageHandler("songrequest.json")
                songtitle = False
                songObject = spotify.getSong(event.input)
                pprint(songObject)
                if songObject != False:
                    songtitle = spotify.addSongToQueue(songObject)
                if songtitle:
                    message = f"{event.user.name} hat '{songtitle}' zur Warteschlange hinzugefügt."
                    await channel.send(message)
                    songerequestStorageHandler.add_entry(id=event.id, spotifyid=songObject["id"], artist=songObject["artists"][0]["name"], songname=songObject["name"], username=event.user.name)
                    self.reward_update_status(event.reward.id, event.id, "FULFILLED")
                else:
                    message = f"Sorry {event.user.name}, der Song {event.input} konnte nicht gefunden werden."
                    await channel.send(message)
                    self.reward_update_status(event.reward.id, event.id, "CANCELED")
            case "Add Song to Playlist":
                songtitle = False
                songObject = spotify.getSong(event.input)
                inPlaylist = False
                if songObject != False:
                    inPlaylist = spotify.searchInPlaylist(songObject, self.config["spotify_playlist_id"])
                    print("inPlaylist: " + str(inPlaylist))
                    if not inPlaylist:
                        print("not inPlaylist")
                        songtitle = spotify.addSongToQueue(songObject)
                        spotify.addSongToPlaylist(songObject, self.config["spotify_playlist_id"])
                print("songtitle: " + str(songtitle))
                if songtitle:
                    message = f"{event.user.name} hat '{songtitle}' zur Playlist hinzugefügt."
                    await channel.send(message)
                    self.reward_update_status(event.reward.id, event.id, "FULFILLED")
                else:
                    if inPlaylist:
                        message = f"Sorry {event.user.name}, der Song {event.input} ist bereits in der Playlist."
                    else:
                        message = f"Sorry {event.user.name}, der Song {event.input} konnte nicht gefunden werden."
                    await channel.send(message)
                    self.reward_update_status(event.reward.id, event.id, "CANCELED")
            

    # define function reward_update_status to update the status of a reward via http request
    def reward_update_status(self, rewardId, redemption_id, status):
        url = f"https://api.twitch.tv/helix/channel_points/custom_rewards/redemptions?broadcaster_id={self.user_channel_id}&reward_id={rewardId}&status={status}&id={redemption_id}"
        headers = {
            "Authorization": f"Bearer {self.user_oauth_token}",
            "Client-Id": self.config["twitch_client_id"]
        }
        response = requests.patch(url, headers=headers)
        pprint(response.json())

    def play_tts_message(self, message):
        urlencode = urllib.parse.quote(message)
        print(urlencode)
        
        # Download the .wav file
        response = requests.get(f"https://{self.config['http_basic_user']}:{self.config['http_basic_password']}@gametts.public.lvl13mage.live?speaker_id=26&text={urlencode}")
        with open('message.wav', 'wb') as f:
            f.write(response.content)

        # Load and play the .wav file
        wave_obj = sa.WaveObject.from_wave_file('message.wav')
        play_obj = wave_obj.play()
        play_obj.wait_done()

        # Delete the .wav file
        os.remove('message.wav')



    