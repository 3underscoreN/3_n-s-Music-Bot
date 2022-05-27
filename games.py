from ast import alias
import discord
from discord.ext import commands
import asyncio

class games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(alias = ["ttt"])
    async def TicTacToe(self,ctx,player1,player2):
        pass

def setup(bot):
    bot.add_cog(games(bot))