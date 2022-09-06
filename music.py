import disnake
from disnake.ext import commands
import pafy
import asyncio
from urllib.parse import urlparse
import youtube_search

FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

# INIT:
playList = []
playTitle = []
playUser = []
playTime = []
buffer = []
channel = ""
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
        global playList
        global playTitle
        global playUser
        global playTime
        global channel
        global FFMPEG_OPTS
        if len(playList) == 1:
            playList = []
            playTitle = []
            playUser = []
            playTime = []
        else:
            try: 
                del playList[0]
                del playTitle[0]
                del playUser[0]
                del playTime[0]
                url = playList[0]
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
        global playList
        global playTitle
        global playUser
        global playTime
        playList = []
        playTitle = []
        playUser = []
        playTime = []
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
            
    @commands.command(aliases = ["lv", "l", "dc", "disconnect", "stop"])
    @commands.guild_only()
    async def leave(self,ctx):
        global playList
        global playTitle
        global playUser
        global playTime
        await ctx.voice_client.disconnect()
        playList.clear()
        playTitle.clear()
        playUser.clear()
        playTime.clear()
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


    @commands.command(aliases = ["p"])
    @commands.guild_only()
    async def play(self,ctx,*,url):
      global playList
      global channel
      global playTitle
      global playUser
      global playTime
      global FFMPEG_OPTS
      if not(ctx.author.voice.channel is None):
          if ctx.voice_client is None:
              await ctx.author.voice.channel.connect()
          videourl = url.split('&', 1)[0]
          channel = ctx.channel
          if playList == []: # No song is playing in vc
            ctx.voice_client.stop()
            vc = ctx.voice_client
            embed = disnake.Embed(title = "Loading...", color = 0x0000ff)
            embed.set_footer(text = "Play • Bot made by 3_n#7069")
            try:
              info = pafy.new(videourl)
              embed.add_field(name = "The bot has identified the URL.", value = "Hold on while the bot parses the URL...")
              message = await ctx.send(embed = embed)
            except:
              try:
                embed.add_field(name = "The bot cannot identify the URL.", value = "Hold on while the bot searches YouTube for appropriate videos...")
                searchResult = "https://www.youtube.com/watch?v=" + youtube_search.YoutubeSearch(videourl, max_results = 1).to_dict()[0]["id"]
                info = pafy.new(searchResult)
                message = await ctx.send(embed = embed)
              except:
                raise urlInvalid(url)
            filename = info.getbestaudio().url
            source = disnake.FFmpegPCMAudio(filename, **FFMPEG_OPTS)
            vc.play(source = source, after = lambda e: self.playnext(ctx))
            playList.append(videourl)
            playTitle.append(info.title)
            playTime.append(info.length)
            playUser.append(ctx.author.name)
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
              message = await ctx.send(embed = embed)
            except:
              try:
                embed.add_field(name = "The bot cannot identify the URL.", value = "Hold on while the bot searches YouTube for appropriate videos...")
                searchResult = "https://www.youtube.com/watch?v=" + youtube_search.YoutubeSearch(videourl, max_results = 1).to_dict()[0]["id"]
                info = pafy.new(searchResult)
                message = await ctx.send(embed = embed)
              except:
                raise urlInvalid(url)
            playList.append(info.watchv_url)
            title = info.title
            playTitle.append(title)
            playTime.append(info.length)
            playUser.append(ctx.author.name)
            embed = disnake.Embed(title = "Success", color = 0x00ff00)
            embed.add_field(name = f'"**{title}**" has been added into the playlist.', value = f"It is currently in queue with a positon of {len(playTitle) - 1}.\nYou can check the whole queue with command `k!queue`.")
            embed.set_footer(text = "Play • Bot made by 3_n#7069")
            await message.edit(embed = embed)
      else:
          await ctx.send("Please be in a voice channel first!")

    @play.error
    async def play_error(self, ctx, error):
      if isinstance(error.__cause__, urlInvalid):
        embed=disnake.Embed(title="Error: Invalid URL", color=0xff0000)
        embed.add_field(name="It seems like the URL is invalid", value="This bot fetches information via the 11-character video ID (should be in your URL in a format of `?watch=<11-character ID>`). Please check if it is present in your URL. If you believe this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).", inline=False)
        embed.set_footer(text="Bot made by 3_n#7069")
        await ctx.send(embed=embed)
        raise ExceptionResolved
      
    @commands.command()
    @commands.guild_only()
    async def pause(self,ctx):
      ctx.voice_client.pause()
      await ctx.send("Paused!")

    @commands.command()
    @commands.guild_only()
    async def resume(self,ctx):
      ctx.voice_client.resume()
      await ctx.send("Resumed!")

    @commands.command()
    @commands.guild_only()
    async def skip(self,ctx):
      ctx.voice_client.stop()
      await ctx.send("Skipped!")

    @commands.command(aliases = ["rmall", "rma", "delall", "deleteall", "dela"])
    @commands.guild_only()
    async def removeall(self, ctx):
        global playList
        global playTitle
        global playUser
        global playTime
        embed = disnake.Embed(title = "Confirmation", color = 0xff0000)
        embed.add_field(name = "Are you sure??", value = "If you delete everything in the queue now, they cannot be added back! You will lost everything in it, ~~including one free Alex moan sound!~~\nType `yes` or `y` to confirm your choice without command prefixes. Uppercase will also work.\nThe bot will cancel the operation if no response is receiveed in 30 seconds.")
        embed.set_footer(text = "RemoveAll • Bot made by 3_n#7069")
        message = await ctx.send(embed = embed)
        try: 
          response = await self.bot.wait_for("message", check = lambda message: message.author == ctx.author, timeout = 30.0)
          if (response.content.lower() in ["yes", "y"]):
            del playList[1:]
            del playTime[1:]
            del playTitle[1:]
            del playUser[1:]
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
      except:
        raise commands.UserInputError
      global playList
      global playTime
      global playTitle
      global playUser
      global buffer
      del playList[intindex]
      del playTime[intindex]
      del playTitle[intindex]
      del playUser[intindex]
      embed = disnake.Embed(title = "Success", color = 0x00ff00)
      embed.add_field(name = "The song has been removed.", value = "Don't worry, you can always add more songs!")
      embed.set_footer(text = "Remove • Bot made by 3_n#7069")
      await ctx.send(embed = embed)

    @commands.command(aliases = ["q", "list", "ls"])
    @commands.guild_only()
    async def queue(self,ctx):
      embed = disnake.Embed(color=0x11f1f5, title = "Song Queue: ")
      if len(playList) > 1:
        for i in range(1, len(playList)):
          embed.add_field(name="{0}: {1}".format(i, playTitle[i]), value="Added by: {0}\nDuration: [{1}:{2:02d}]\n[(Click here to open on YouTube)]({3})".format(playUser[i], playTime[i]//60, playTime[i] % 60, playList[i]), inline=False)
        TotalPlayTime = sum(playTime) - playTime[0]
        embed.set_footer(text="Song Queue • Total Duration: {0}:{1:02d} • Bot made by 3_n#7069".format(TotalPlayTime//60,TotalPlayTime%60))
        await ctx.send(embed=embed)
      else:
        await ctx.send("There are no songs in the queue.")

    @commands.command(aliases = ["np"])
    @commands.guild_only()
    async def nowplaying(self,ctx):
      try:
        embed = disnake.Embed(title="**Now playing: **", color=0x11f1f5)
        info = pafy.new(playList[0])
        embed.set_thumbnail(url=info.thumb)
        embed.add_field(name="{0}".format(playTitle[0], playList[0]), value="([Play on YouTube]({3}))\nAdded by {0}\nDuration: [{1}:{2:02d}]".format(playUser[0] ,playTime[0]//60 ,playTime[0] % 60, playList[0]), inline=False)
        embed.set_footer(text="Now playing • Bot made by 3_n#7069")
        await ctx.send(embed = embed)
      except(IndexError):
        await ctx.send("There are no currently playing songs.")

def setup(bot):
    bot.add_cog(music(bot))

if __name__ == "__main__":
    print("This is not the main script! Run main.py")