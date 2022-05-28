import discord
from discord.ext import commands
import youtube_dl
import asyncio
from urllib.parse import urlparse

YDL_OPTIONS = {"format":"bestaudio"}

# INIT:
playList = []
playTitle = []
playUser = []
playTime = []
channel = ""
# INIT END

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def playnext(self, ctx):
      global playList
      global playTitle
      global playUser
      global playTime
      global channel
      if len(playList) == 1:
        playList = []
        playTitle = []
        playUser = []
        playTime = []
      else:
        try: 
          playList.pop(0)
          playTitle.pop(0)
          playUser.pop(0)
          playTime.pop(0)
          url = playList[0]
          ctx.voice_client.stop()
          vc = ctx.voice_client
          with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download = False)
            ydlurl = info["formats"][0]["url"]
            source = discord.FFmpegOpusAudio(ydlurl, before_options = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
            vc.play(source = source, after=lambda e: self.playnext(ctx))
        except:
          pass

    @commands.command(aliases = ["j"])
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
    async def leave(self,ctx):
        global playList
        global playTitle
        global playUser
        global playTime
        await ctx.voice_client.disconnect()
        playList = []
        playTitle = []
        playUser = []
        playTime = []
        await ctx.send("Voice channel left and queue is emptied.")

    @commands.command(aliases = ["p"])
    async def play(self,ctx,url):
        if not(ctx.author.voice.channel is None):
          if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
          videourl = url.split('&', 1)[0]
          global playList
          global YDL_OPTIONS
          global channel
          global playTitle
          global playUser
          global playTime
          channel = ctx.channel
          if playList == []:
            playList.append(videourl)
            ctx.voice_client.stop()
            vc = ctx.voice_client 
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(videourl, download = False)
                ydlurl = info["formats"][0]["url"]
                playTitle.append(info.get('title', None))
                playTime.append(info["duration"])
                playUser.append(ctx.author.name)
                source = discord.FFmpegOpusAudio(ydlurl, before_options = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
                await ctx.send("Loading...")
                await asyncio.sleep(1)
                vc.play(source = source, after=lambda e: self.playnext(ctx))
                await ctx.send("Playing music now.")
                #print(playTitle[0])
                #print(playTime[0])
                #print(playUser[0])
          else:
            playList.append(videourl)
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
              info = ydl.extract_info(videourl, download = False)
              playTitle.append(info.get('title', None))
              playTime.append(info["duration"])
              playUser.append(ctx.author.name)
            await ctx.send("Song added to playlist!")
        else:
          await ctx.send("Please be in a voice channel first!")

    @commands.command()
    async def pause(self,ctx):
      ctx.voice_client.pause()
      await ctx.send("Paused!")

    @commands.command()
    async def resume(self,ctx):
      ctx.voice_client.resume()
      await ctx.send("Resumed!")

    @commands.command()
    async def skip(self,ctx):
        ctx.voice_client.stop()
        await ctx.send("Skipped!")

    @commands.command(aliases = ["q", "list", "ls"])
    async def queue(self,ctx):
      embed = discord.Embed(color=0x11f1f5)
      if len(playList) > 1:
        for i in range(1, len(playList)):
          embed.add_field(name="{0}: {1}".format(i, playTitle[i]), value="Added by: {0}\nDuration: [{1}:{2:02d}]".format(playUser[i], playTime[i]//60, playTime[i] % 60), inline=False)
        TotalPlayTime = sum(playTime) - playTime[0]
        embed.set_footer(text="Song Queue • Total Duration: {0}:{1} • Bot made by 3_n#7069".format(TotalPlayTime//60,TotalPlayTime%60))
        await ctx.send(embed=embed)
      else:
        await ctx.send("There are no songs in the queue.")

    @commands.command(aliases = ["np"])
    async def nowplaying(self,ctx):
      try:
        embed = discord.Embed(title="**Now playing: **", color=0x11f1f5)
        embed.add_field(name="{0}".format(playTitle[0]), value="Added by {0}\nDuration: [{1}:{2:02d}]".format(playUser[0] ,playTime[0]//60 ,playTime[0] % 60), inline=False)
        embed.set_footer(text="Now playing • Bot made by 3_n#7069")
        await ctx.send(embed = embed)
      except(IndexError):
        await ctx.send("There are no currently playing songs.")

def setup(bot):
    bot.add_cog(music(bot))