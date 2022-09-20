from smtplib import quoteaddr
import disnake
import os
from disnake.ext import commands
import pafy
import asyncio
from urllib.parse import urlparse
import youtube_search


FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

# INIT:
# playList = []
# playTitle = []
# playUser = []
# playTime = [] # Those variables are not used anymore
playQueue = [] # should contain lists with [URL (str), Title (str), User (str), Duration (int)]

channel = ""
repeatMode = 0 # 0 = normal, 1 = single, 2 = list
# INIT END

class urlInvalid(Exception):
    def __init__(self, url):
        self.url = url

class ExceptionResolved(Exception):
    pass

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    def playnext(self, ctx):
        global repeatMode
        global playQueue
        global channel
        global FFMPEG_OPTS
        try:
            if len(playQueue) == 1:
                if not repeatMode in [1, 2]:
                    playQueue.clear()
                else:
                    ctx.voice_client.stop()
                    vc = ctx.voice_client
                    info = pafy.new(playQueue[0][0])
                    filename = info.getbestaudio().url
                    source = disnake.FFmpegPCMAudio(filename, **FFMPEG_OPTS)
                    vc.play(source = source, after = lambda e:self.playnext(ctx))
            else:
                if repeatMode == 0:
                    del playQueue[0]
                    url = playQueue[0][0]
                if repeatMode == 2:
                    playQueue.append(playQueue.pop(0))
                    url = playQueue[0][0]
                if repeatMode == 1:
                    url = playQueue[0][0]
                ctx.voice_client.stop()
                vc = ctx.voice_client
                info = pafy.new(url)
                filename = info.getbestaudio().url
                source = disnake.FFmpegPCMAudio(filename, **FFMPEG_OPTS)
                vc.play(source = source, after = lambda e: self.playnext(ctx))
        except:
            pass

    @commands.command(aliases = ["j"])
    @commands.guild_only()
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
            embed = disnake.Embed(title = "Success", color = 0x00ff00)
            embed.add_field(name = "The bot has joined your current voice channel", value = "You can start playing music but using the command `k!play <Youtube URL>`!")
            embed.set_footer(text="Join • Bot made by 3_n#7069")
            await ctx.send(embed = embed)
        else:
            embed = disnake.Embed(title = "Error: Bot in another voice channel", color = 0xff0000)
            embed.add_field(name = "It seems like the bot is in another voice channel now.", value = "Please use `k!leave` first.\nIf you think this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).")
            embed.set_footer(text = "Bot made by 3_n#7069")
            await ctx.send(embed = embed)

    @join.error
    async def join_error(self, ctx, error):
        if isinstance(error.__cause__, AttributeError):
            embed = disnake.Embed(title = "Error: User not in voice channel", color = 0xff0000)
            embed.add_field(name = "It seems like your are not in a voice channel.", value = "Please join a voice channel before I can blast music there.\nIf you believe this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).")
            embed.set_footer(text = "Bot made by 3_n#7069")
            await ctx.send(embed = embed)
            raise ExceptionResolved

    @commands.command(aliases = ["lv", "l", "dc", "disconnect", "stop"])
    @commands.guild_only()
    async def leave(self,ctx):
        global playQueue
        await ctx.voice_client.disconnect()
        playQueue.clear()
        embed = disnake.Embed(title = "Success", color = 0x00ff00)
        embed.add_field(name = "The bot has left the voice channel.", value = "The queue is also cleared. If you want to vibe with music again, you can use `k!join`!")
        embed.set_footer(text = "Leave • Bot made by 3_n#7069")
        await ctx.send(embed = embed)

    @leave.error
    async def leave_error(self, ctx, error):
        if isinstance(error.__cause__, AttributeError):
            embed = disnake.Embed(title = "Error: Not in a Voice Channel", color = 0xff0000)
            embed.add_field(name = "It seems like the bot is not in any voice channels.", value = "The command can only be use when the bot is in a voice channel.\nIf you believe this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).")
            embed.set_footer(text="Bot made by 3_n#7069")
            await ctx.send(embed = embed)
            raise ExceptionResolved

    @commands.command(aliases = ["s"])
    @commands.guild_only()
    async def search(self, ctx, *, keyword):
        query = youtube_search.YoutubeSearch(keyword, max_results = 5).to_dict()
        embed = disnake.Embed(title = f"Search results of `{keyword}`", color = 0x11f1f5)
        for i in range(5):
            embed.add_field(name = "{0}: {1}".format(i + 1, query[i]["title"]), value = "Uploaded by: {0}\nDuration: {1}\n[Click here to view on YouTube]({2})".format(query[i]["channel"], query[i]["duration"], "https://www.youtube.com{0}".format(query[i]["url_suffix"])), inline = False)
        embed.set_footer(text = "Search • Bot made by 3_n#7069")
        await ctx.send("Below are the results of the search. If you want to directly play a specific song, enter the index (such as 1) directly without any prefixes.", embed = embed)
        try:
            playIndex = await self.bot.wait_for("message", check = lambda message: message.author == ctx.author, timeout = 20.0)
            videourl = "https://www.youtube.com{0}".format(query[int(playIndex.content) - 1]["url_suffix"])
            await ctx.invoke(self.bot.get_command("play"), url = videourl)
        except Exception as e:
            if isinstance(e, asyncio.TimeoutError) or isinstance(e, ValueError) or isinstance(e, IndexError):
                pass
            else:
                raise e

    @commands.command(aliases = ["p"])
    @commands.guild_only()
    async def play(self, ctx, *, url):
        embed = disnake.Embed(title = "Loading...", color = 0x0000ff)
        embed.add_field(name = "Processing...", value = "The bot is processing your command.\nIf you are stuck in this embed, most likely the bot went into a problem and error handling didn't catch it.\nPlease open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot) if that happens.")
        embed.set_footer(text = "Play • Bot made by 3_n#7069")
        message = await ctx.send(embed = embed)
        global playQueue
        global channel
        global FFMPEG_OPTS
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
        videourl = url.split('&', 1)[0]
        channel = ctx.channel
        if playQueue == []: # No song is playing in vc
            ctx.voice_client.stop()
            vc = ctx.voice_client
            embed = disnake.Embed(title = "Loading...", color = 0x0000ff)
            embed.set_footer(text = "Play • Bot made by 3_n#7069")
            try:
                info = pafy.new(videourl)
                embed.add_field(name = "The bot has identified the URL.", value = "Hold on while the bot parses the URL...")
                await message.edit(embed = embed)
            except (ValueError, OSError): 
            # sometimes OSError is thrown instead of valueError when songs cannot be searched (mostly when non-ascii characters is inputted)
                try:
                    embed.add_field(name = "The bot is searching on YouTube", value = f"Hold on while the bot searches {videourl} on YouTube.")
                    searchResult = "https://www.youtube.com{0}".format(youtube_search.YoutubeSearch(videourl, max_results = 1).to_dict()[0]["url_suffix"])
                    info = pafy.new(searchResult)
                    await message.edit(embed = embed)
                except OSError:
                    embed = disnake.Embed(title = "Error: Unable to play video", color = 0xff0000)
                    embed.add_field(name = "The video requested cannot be played.", value = "That means the video is probably private, deleted and probably age-restricted, meaning that you can't play 夜に駆ける. :sob:\nI am trying to find a way through this.\nIf you believe this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).")
                    embed.set_footer(text = "Play • Bot made by 3_n#7069")
                    await message.edit(embed = embed)
                    return
                except:
                    raise urlInvalid(url)
            filename = info.getbestaudio().url
            source = disnake.FFmpegPCMAudio(filename, **FFMPEG_OPTS)
            vc.play(source = source, after = lambda e: self.playnext(ctx))
            playQueue.append([info.watchv_url, info.title, ctx.author.name, info.length])
            # playList.append(info.watchv_url)
            # playTitle.append(info.title)
            # playTime.append(info.length)
            # playUser.append(ctx.author.name)
            await asyncio.sleep(0.25)
            embed = disnake.Embed(title = "Success", color = 0x00ff00)
            embed.add_field(name = f'"{info.title}" has been added into the playlist.', value = "It will be played instantly.")
            embed.set_footer(text = "Play • Bot made by 3_n#7069")
            await message.edit(embed = embed)
        else: #add song to queue as there's a song playing in vc
            embed = disnake.Embed(title = "Loading...", color = 0x0000ff)
            embed.set_footer(text = "Play • Bot made by 3_n#7069")
            try:
                info = pafy.new(videourl)
                embed.add_field(name = "The bot has identified the URL.", value = "Hold on while the bot parses the URL...")
                await message.edit(embed = embed)
            except:
                try:
                    embed.add_field(name = "The bot cannot identify the URL.", value = "Hold on while the bot searches YouTube for appropriate videos...")
                    searchResult = "https://www.youtube.com/watch?v=" + youtube_search.YoutubeSearch(videourl, max_results = 1).to_dict()[0]["id"]
                    info = pafy.new(searchResult)
                    await message.edit(embed = embed)
                except OSError:
                    embed = disnake.Embed(title = "Error: Unable to fetch video", color = 0xff0000)
                    embed.add_field(name = "The video requested cannot be fetched.", value = "That means the video is probably private, deleted and probably age-restricted, meaning that you can't play 夜に駆ける. :sob:\nI am trying to find a way through this.\nIf you believe this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).")
                    embed.set_footer(text = "Play • Bot made by 3_n#7069")
                    await message.edit(embed = embed)
                    return
                except:
                    raise urlInvalid(url)
            # playList.append(info.watchv_url)
            title = info.title
            # playTitle.append(title)
            # playTime.append(info.length)
            # playUser.append(ctx.author.name)
            playQueue.append([info.watchv_url, title, ctx.author.name, info.length])
            embed = disnake.Embed(title = "Success", color = 0x00ff00)
            embed.add_field(name = f'"**{title}**" has been added into the queue.', value = f"It is currently in queue with a positon of {len(playQueue) - 1}.\nYou can check the whole queue with command `k!queue`.")
            embed.set_footer(text = "Play • Bot made by 3_n#7069")
            await message.edit(embed = embed)

    @play.error
    async def play_error(self, ctx, error):
        if isinstance(error.__cause__, urlInvalid):
            embed=disnake.Embed(title="Error: Invalid URL", color=0xff0000)
            embed.add_field(name="It seems like the URL is invalid", value="This bot fetches information via the 11-character video ID (should be in your URL in a format of `?watch=<11-character ID>`). Please check if it is present in your URL. If you believe this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).", inline=False)
            embed.set_footer(text="Bot made by 3_n#7069")
            await ctx.send(embed=embed)
            raise ExceptionResolved
        elif isinstance(error.__cause__, AttributeError):
            embed = disnake.Embed(title = "Error: User not in voice channel", color = 0xff0000)
            embed.add_field(name = "It seems like your are not in a voice channel.", value = "Please join a voice channel before I can blast music there.\nIf you believe this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).")
            embed.set_footer(text = "Bot made by 3_n#7069")
            await ctx.send(embed = embed)
            raise ExceptionResolved

    @commands.command()
    @commands.guild_only()
    async def pause(self,ctx):
        embed = disnake.Embed(title = "Success", color = 0x00ff00)
        embed.add_field(name = "The song has been paused", value = "You can resume playing with `k!resume`.")
        embed.set_footer(text = "Pause • Bot made by 3_n#7069")
        ctx.voice_client.pause()
        await ctx.send(embed = embed)

    @commands.command()
    @commands.guild_only()
    async def resume(self,ctx):
        embed = disnake.Embed(title = "Success", color = 0x00ff00)
        embed.add_field(name = "The song has been resumed.", value = "You can pause playing with `k!pause`, or skip the song with `k!skip`.")
        embed.set_footer(text = "Resume • Bot made by 3_n#7069")
        ctx.voice_client.resume()
        await ctx.send(embed = embed)

    @commands.command()
    @commands.guild_only()
    async def skip(self,ctx):
        embed = disnake.Embed(title = "Success", color = 0x00ff00)
        if len(playQueue) > 1 and repeatMode in [0, 2]:
            embed.add_field(name = "Current song has been skipped.", value = f'The next song in queue, "**{playQueue[1][1]}**" will start playing now.')
        elif repeatMode == 1:
            embed.add_field(name = "Current song has been skipped.", value = "However, as repeat mode is single right now, the song will start playing again. There's no escape now.")
        elif len(playQueue) == 1 and repeatMode == 2:
            embed.add_field(name = "Current song has been skipped.", value = "However, as repeat mode is queue and there's only 1 song in the queue, the song will start playing again. There's no escape now.")
        else:
            embed.add_field(name = "Current song has been skipped.", value = "There are no other songs in queue now. Playing will be stopped now.")
        embed.set_footer(text = "Pause • Bot made by 3_n#7069")
        ctx.voice_client.stop()
        await ctx.send(embed = embed)

    @commands.command(aliases = ["rmall", "rma", "delall", "deleteall", "dela"])
    @commands.guild_only()
    async def removeall(self, ctx):
        global playQueue
        # global playTitle
        # global playUser
        # global playTime
        embed = disnake.Embed(title = "Confirmation", color = 0xff0000)
        embed.add_field(name = "Are you sure??", value = "If you delete everything in the queue now, they cannot be added back! You will lost everything in it, ~~including one free Alex moan sound!~~\nType `yes` or `y` to confirm your choice without command prefixes. Uppercase will also work.\nThe bot will cancel the operation if no response is receiveed in 30 seconds.")
        embed.set_footer(text = "RemoveAll • Bot made by 3_n#7069")
        message = await ctx.send(embed = embed)
        try: 
            response = await self.bot.wait_for("message", check = lambda message: message.author == ctx.author, timeout = 30.0)
            if (response.content.lower() in ["yes", "y"]):
                del playQueue[1:]
                # del playTime[1:]
                # del playTitle[1:]
                # del playUser[1:]
                embed = disnake.Embed(title = "Success", color = 0x00ff00)
                embed.add_field(name = "All songs in the queue has been removed.", value = "Don't worry, you can always add more songs!")
                embed.set_footer(text = "RemoveAll • Bot made by 3_n#7069")
                await message.edit(embed = embed)
            else:
                embed = disnake.Embed(title = "Operation Cancelled", color = 0xffff00)
                embed.add_field(name = "No songs are deleted from the queue.", value = "As you sent something other than ""yes"" or ""y"", the operation is cancelled.")
                embed.set_footer(text = "RemoveAll • Bot made by 3_n#7069")
                await message.edit(embed = embed)
        except asyncio.TimeoutError:
            embed = disnake.Embed(title = "Operation Cancelled", color = 0xffff00)
            embed.add_field(name = "No songs are deleted from the queue.", value = "As you did not send anything within 30 seconds, the operation is automatically cancelled.")
            embed.set_footer(text = "RemoveAll • Bot made by 3_n#7069")
            await message.edit(embed = embed)

    @commands.command(aliases = ["rm", "del", "delete"])
    @commands.guild_only()
    async def remove(self, ctx, index):
        try:
            intindex = int(index)
            if intindex == 0:
                raise Exception
        except:
            raise commands.UserInputError
        global playQueue
        # global playTime
        # global playTitle
        # global playUser
        del playQueue[intindex]
        # del playTime[intindex]
        # del playTitle[intindex]
        # del playUser[intindex]
        embed = disnake.Embed(title = "Success", color = 0x00ff00)
        embed.add_field(name = "The song has been removed.", value = "Don't worry, you can always add more songs!")
        embed.set_footer(text = "Remove • Bot made by 3_n#7069")
        await ctx.send(embed = embed)

    @commands.command(aliases = ["q", "list", "ls"])
    @commands.guild_only()
    async def queue(self,ctx):
        embed = disnake.Embed(color=0x11f1f5, title = "Song Queue: ")
        if len(playQueue) > 1:
            TotalPlayTime = 0
            for i in range(1, len(playQueue)):
                embed.add_field(name=f"{i}: {playQueue[i][1]}", value="Added by: {0}\nDuration: [{1}:{2:02d}]\n[(Click here to open on YouTube)]({3})".format(playQueue[i][2], playQueue[i][3]//60, playQueue[i][3] % 60, playQueue[i][0]), inline=False)
                TotalPlayTime += playQueue[i][3]
                # TotalPlayTime = sum(playTime) - playTime[0]
                embed.set_footer(text="Song Queue • Total Duration: {0}:{1:02d} • Bot made by 3_n#7069".format(TotalPlayTime//60,TotalPlayTime%60))
            await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(title = "Error: No songs in queue", color = 0xff0000)
            embed.add_field(name = "There are no songs in the queue.", value = "However you can add songs with `k!play <YouTube URL/keyword>`!")
            embed.set_footer(text = "Queue • Bot made by 3_n")
            await ctx.send(embed = embed)

    @commands.command(aliases = ["r"])
    @commands.guild_only()
    async def repeat(self, ctx, newRepeatMode = "None"):
        global repeatMode
        if newRepeatMode.lower() in ["0", "n", "normal", "no", "off"]:
            newRepeatMode = 0
        elif newRepeatMode.lower() in ["1", "s", "single", "loop", "brainwash"]:
            newRepeatMode = 1
        elif newRepeatMode.lower() in ["2", "loopqueue", "queue", "list", "q", "ls"]:
            newRepeatMode = 2
        if newRepeatMode == "None": 
            embed = disnake.Embed(title = "Repeat status: ", color = 0x00ff00)
            if repeatMode == 0:
                embed.add_field(name = "Normal", value = "This bot is not repeating any music.\nYou can change it to repeat 1 song or multiple songs by `k!repeat [single/queue]`!")
            elif repeatMode == 1:
                embed.add_field(name = "Single", value = "This bot is constantly repeating one single song ~~to brainwash everyone here~~.\nYou can change it to not repeat songs or repeat the queue instead by `k!repeat [normal/queue]`!")
            elif repeatMode == 2:
                embed.add_field(name = "Queue", value = "The bot is repeating the queue (which can be checked by entering `k!queue`, however the current song will also be included).\nYou can change it to not repeat or repeat one song only by `k!repeat[normal/single]`!")
        elif newRepeatMode in [0, 1, 2]:
            repeatMode = newRepeatMode
            embed = disnake.Embed(title = "Success", color = 0x00ff00)
            if repeatMode == 0:
                embed.add_field(name = "Curreny Mode: Normal", value = "This bot is now not repeating any music.\nYou can change it to repeat 1 song or multiple songs by `k!repeat [single/queue]`!")
            elif repeatMode == 1:
                embed.add_field(name = "Current Mode: Single", value = "This bot is now constantly repeating one single song.\nYou can change it to not repeat songs or repeat the queue instead by `k!repeat [normal/queue]`!")
            elif repeatMode == 2:
                embed.add_field(name = "Current Mode: Queue", value = "The bot is now repeating the queue (which can be checked by entering `k!queue`, however the current song will also be included).\nYou can change it to not repeat or repeat one song only by `k!repeat[normal/single]`!")
        else:
            raise commands.UserInputError()
        embed.set_footer(text = "Repeat • Bot made by 3_n#7069")
        await ctx.send(embed = embed)

    @commands.command(aliases = ["np"])
    @commands.guild_only()
    async def nowplaying(self,ctx):
        try:
            embed = disnake.Embed(title="**Now playing: **", color=0x11f1f5)
            info = pafy.new(playQueue[0][0])
            embed.set_thumbnail(url=info.thumb)
            embed.add_field(name=f"{playQueue[0][1]}", value="([Play on YouTube]({3}))\nAdded by {0}\nDuration: [{1}:{2:02d}]".format(playQueue[0][2] ,playQueue[0][3]//60 ,playQueue[0][3] % 60, playQueue[0][0]), inline=False)
            embed.set_footer(text="Now playing • Bot made by 3_n#7069")
            await ctx.send(embed = embed)
        except(IndexError):
            embed = disnake.Embed(title = "Error: No songs currently playing.", color = 0xff0000)
            embed.add_field(name = "The bot is not playing any songs.", value = "However you can always start playing with `k!play <YouTube URL/Keywords>`!")
            embed.set_footer(text = "Now playing • Bot made by 3_n#7069")
            await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(music(bot))

if __name__ == "__main__":
    print("This is not the main script! Run main.py")