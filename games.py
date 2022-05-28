import discord
from discord.ext import commands
import asyncio
import random
import json, os

directory = os.getcwd()

wordList = json.loads(open(f"{directory}/games/wordle.json").read())

class games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def wordle(self, ctx):
        player = ctx.author
        answer = random.choice(wordList).lower()
        guessCount = 0
        await ctx.author.send("This feature is currently under development. Stay tuned!")

def setup(bot):
    bot.add_cog(games(bot))