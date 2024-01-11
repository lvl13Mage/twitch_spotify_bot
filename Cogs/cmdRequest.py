from twitchio.ext import commands
from Spotify.spotifyClient import SpotifyClient
from pprint import pprint
from JsonPersistence.jsonSongerequestStorageHandler import JsonSongRequestStorageHandler

class CmdRequest(commands.Cog):

    def __init__(self, bot: commands.Bot, config):
        self.bot = bot
        self.config = config

        self.number_emojis = [
            "1\uFE0F\u20E3",
            "2\uFE0F\u20E3",
            "3\uFE0F\u20E3",
            "4\uFE0F\u20E3",
            "5\uFE0F\u20E3",
            "6\uFE0F\u20E3",
            "7\uFE0F\u20E3",
            "8\uFE0F\u20E3",
            "9\uFE0F\u20E3",
            "1\uFE0F\u20E30\uFE0F\u20E3"
        ]

    @commands.command(name="songrequest", aliases=["sr"])
    @commands.cooldown(rate=1, per=25, bucket=commands.Bucket.user)
    async def songrequest(self, ctx: commands.Context, *, songname: str):
        if self.config["request_command"] != 'true':
            return
        spotify = SpotifyClient(self.config)
        songtitle = False
        songObject = spotify.getSong(songname)
        pprint(songObject)
        if songObject != False:
            songtitle = spotify.addSongToQueue(songObject)
        if songtitle:
            message = f"{ctx.author.name} hat '{songtitle}' zur Warteschlange hinzugefügt."
            await ctx.send(message)
        else:
            message = f"Sorry {ctx.author.name}, der Song {songname} konnte nicht gefunden werden."
            await ctx.send(message)

    @commands.command(name="queue", aliases=["sq", "songqueue"])
    @commands.cooldown(rate=1, per=25, bucket=commands.Bucket.user)
    async def queue(self, ctx: commands.Context):
        spotify = SpotifyClient(self.config)
        queue = spotify.getQueue()
        queue_output = [""]
        linecount = 0
        for i in range(len(queue)):
            lenQueueOutput = len(queue_output[linecount])
            lenQueueItem = len(queue[i])
            if lenQueueOutput + lenQueueItem >= 399:
                linecount += 1
                queue_output.append("")
            queue_output[linecount] += f"{self.number_emojis[i]} {queue[i]} "
        for line in range(len(queue_output)):
            await ctx.send(f"Die nächsten 10 Songs sind: {queue_output[line]}")
    
    @commands.command(name="lastsongs", aliases=["ls"])
    @commands.cooldown(rate=1, per=25, bucket=commands.Bucket.user)
    async def lastsongs(self, ctx: commands.Context):
        spotify = SpotifyClient(self.config)
        lastsongs = spotify.getLastSongs()
        lastsongs_output = [""]
        linecount = 0
        for i in range(len(lastsongs)):
            lenQueueOutput = len(lastsongs_output[linecount])
            lenQueueItem = len(lastsongs[i])
            if lenQueueOutput + lenQueueItem >= 399:
                linecount += 1
                lastsongs_output.append("")
            lastsongs_output[linecount] += f"{self.number_emojis[i]} {lastsongs[i]} "
        for line in range(len(lastsongs_output)):
            await ctx.send(f"Die letzten 10 Songs waren: {lastsongs_output[line]}")
        
    @commands.command(name="currentsong", aliases=["cs"])
    @commands.cooldown(rate=1, per=25, bucket=commands.Bucket.user)
    async def currentsong(self, ctx: commands.Context):
        try:
            songRequestHandler = JsonSongRequestStorageHandler("songrequest.json")
            spotify = SpotifyClient(self.config)
            currentSongObject = spotify.getCurrentSongObject()
            currentSong = currentSongObject["artists"][0]["name"] + " - " + currentSongObject["name"]
            songRequestHandler.pop_until_song(currentSongObject["id"])
            useradded = songRequestHandler.fetch_by_spotifyid(currentSongObject["id"])
            pprint(useradded)
            if len(useradded) == 0:
                await ctx.send(f"Der aktuelle Song ist: {currentSong}")
            else:
                await ctx.send(f"Der aktuelle Song ist: {currentSong} -- added by {useradded[0]["username"]}")
        except commands.CommandOnCooldown as e:
            await ctx.send(f"Sorry {ctx.author.name}, der Befehl ist noch auf Cooldown.")

    @commands.command(name="searchsong", aliases=["findsong", "fs"])
    @commands.cooldown(rate=1, per=25, bucket=commands.Bucket.user)
    async def searchsong(self, ctx: commands.Context, *, songname: str):
        spotify = SpotifyClient(self.config)
        results = spotify.searchSong(songname, 5)
        search_output = [""]
        linecount = 0
        for i in range(len(results["tracks"]["items"])):
            lenQueueOutput = len(search_output[linecount])
            lenQueueItem = len(results["tracks"]["items"][i]["name"])
            if lenQueueOutput + lenQueueItem >= 399:
                linecount += 1
                search_output.append("")
            search_output[linecount] += f"{self.number_emojis[i]} {results['tracks']['items'][i]['artists'][0]['name']} - {results['tracks']['items'][i]['name']} -- {results['tracks']['items'][i]['uri']}"
        for line in range(len(search_output)):
            await ctx.send(f"Die ersten 5 Suchergebnisse für '{songname}' sind:\n{search_output[linecount]}")
    
    @commands.command(name="skipsong", aliases=["skip"])
    async def skipsong(self, ctx: commands.Context):
        if not ctx.author.is_mod:
            return
        spotify = SpotifyClient(self.config)
        spotify.skipSong()
        await ctx.send(f"Song wurde übersprungen von {ctx.author.name}.")

    # TODO: does not fucking work
    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        print("Error Handler?")
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.CommandOnCooldown):
            print("foobar")
            await ctx.send(f"Sorry {ctx.author.name}, der Befehl ist noch auf Cooldown.")
            raise error
        else:
            await ctx.send(f"Sorry {ctx.author.name}, es ist ein Fehler aufgetreten.")
            raise error