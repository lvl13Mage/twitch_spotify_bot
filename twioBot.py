from twitchio.ext import commands
import os
import asyncio
from channelPointRewards import ChannelPointRewards

class Bot(commands.Bot):

    def __init__(self, config):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token=config['twitch_access_token'], prefix='!', initial_channels=[config['channel']])
        self.config = config
        self.user = self.getUser()
        
        if config['affiliate'] == 'true':
            self.channelPointRewards = ChannelPointRewards(self, config)

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        if self.config['affiliate'] == 'true':
            await self.enable_rewards()
        # print refresh token
            
    async def event_command_error(self, context: commands.Context, error: Exception):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.CommandOnCooldown):
            await context.send(f"Sorry {context.author.name}, der Befehl ist noch für {error.retry_after:.2f}s auf Cooldown.")
            raise error
        else:
            await context.send(f"Sorry {context.author.name}, es ist ein Fehler aufgetreten.")
            raise error

    async def setup(self):
        self.user = await self.getUser()
        print(f'User is | {self.user.name}')

    def getUser(self):
        return self.create_user(self.config['client_id'],self.config['channel'])
        #return await self.fetch_users(self.config['channel'])

    async def close(self):
        print("Stopping TwioBot...")
        await self.channelPointRewards.disable_reward(self.config['twitch_access_token'], "Song Request", self.config['spotify_channelpoints']['Song Request']['cost'], self.config['spotify_channelpoints']['Song Request']['description'], True, False)
        await self.channelPointRewards.disable_reward(self.config['twitch_access_token'], "Add Song to Playlist", self.config['spotify_channelpoints']['Add Song to Playlist']['cost'], self.config['spotify_channelpoints']['Add Song to Playlist']['description'], True, False)
        print("TwioBot stopped.")

    async def enable_rewards(self):
        print(self.config['spotify_channelpoints']['Song Request']['enabled'])
        print(self.config['spotify_channelpoints']['Add Song to Playlist']['enabled'])
        if self.config['spotify_channelpoints']['Song Request']['enabled']:
            await self.channelPointRewards.enable_reward(self.config['twitch_access_token'], "Song Request", self.config['spotify_channelpoints']['Song Request']['cost'], self.config['spotify_channelpoints']['Song Request']['description'], True, True)
        if self.config['spotify_channelpoints']['Add Song to Playlist']['enabled']:
            await self.channelPointRewards.enable_reward(self.config['twitch_access_token'], "Add Song to Playlist", self.config['spotify_channelpoints']['Add Song to Playlist']['cost'], self.config['spotify_channelpoints']['Add Song to Playlist']['description'], True, True)

