import disnake
from disnake.ext import commands
import pafy
import asyncio
from urllib.parse import urlparse

FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

# INIT:
playList = []
playTitle = []
playUser = []
playTime = []
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
        if channel is None:
          await ctx.send("Please join a voice channel first.")
        elif ctx.voice_client is None:
          await channel.connect()
          await ctx.send("Joined!")
          ctx.voice_client.stop()
        else:
            await ctx.send("The bot is in another channel right now. Use 'leave' first.")
            
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
        await ctx.send("Voice channel left and queue is emptied.")

    @leave.error
    async def leave_error(self, ctx, error):
        if isinstance(error.__cause__, AttributeError):
          embed = disnake.Embed(title = "Error: Not in a Voice Channel", color = 0xff0000)
          embed.add_field(name = "It seems like the bot is not in any voice channels.", value = "The command can only be use when the bot is in a voice channel.\nIf you believe this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot)")
          embed.set_footer(text="Bot made by 3_n#7069")
          await ctx.send(embed = embed)
          raise ExceptionResolved


    @commands.command(aliases = ["p"])
    @commands.guild_only()
    async def play(self,ctx,url):
        if not(ctx.author.voice.channel is None):
          if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
          videourl = url.split('&', 1)[0]
          global playList
          global channel
          global playTitle
          global playUser
          global playTime
          global FFMPEG_OPTS
          channel = ctx.channel
          try:
            if playList == []: # No song is playing in vc
              ctx.voice_client.stop()
              vc = ctx.voice_client
              info = pafy.new(videourl)
              filename = info.getbestaudio().url
              source = disnake.FFmpegPCMAudio(filename, **FFMPEG_OPTS)
              vc.play(source = source, after = lambda e: self.playnext(ctx))
              playList.append(videourl)
              playTitle.append(info.title)
              playTime.append(info.length)
              playUser.append(ctx.author.name)
              await asyncio.sleep(0.5)
              await ctx.send(f"Playing **{info.title}** now.")
              # print(playTitle[0])
              # print(playTime[0])
              # print(playUser[0])
            else: #add song to queue as there's a song playing in vc
              playList.append(videourl)
              info = pafy.new(videourl) #only to fetch video title, thumbnail etc.
              title = info.title
              playTitle.append(title)
              playTime.append(info.length)
              playUser.append(ctx.author.name)
              await ctx.send(f"**{title}** added to playlist!")
          except ValueError:
              raise urlInvalid(url)
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