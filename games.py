import discord
from discord.ext import commands
import asyncio
import random
import json, os
import asyncio

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
        await ctx.send("The word has been generated. Start guessing by typing a 5-letter word! Note that if no input is detected for 60 seconds, the bot timeouts.")
        try:
            for guessCount in range(5):
                message = await self.bot.wait_for("message", check = lambda message: message.author == ctx.author, timeout= 60.0)
                

        except asyncio.TimeoutError():
            await ctx.send(f"As no input is detected, the wordle has ended. The answer is: {answer.lower()}")


def setup(bot):
    bot.add_cog(games(bot))