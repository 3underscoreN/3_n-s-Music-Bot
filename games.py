import discord
from discord.ext import commands
import asyncio
import random
import json, os
import asyncio
import string

directory = os.getcwd()

wordList = json.loads(open(f"{directory}/games/wordle.json").read())

class games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def wordle(self, ctx):
        player = ctx.author
        answer = random.choice(wordList).lower()
        answer2 = list(answer) # answer but correct guess is removed
        guessCount = 0
        correct = False
        embed=discord.Embed(title="The word has been generated.", description="Start guessing by sending a 5-letter word (not in a command form).", color=0x00d5ff)
        embed.add_field(name="Note", value="You can manually terminate the program by sending `exit`.\nThe game will also terminate if no input is detected for 5 minutes.", inline=False)
        embed.set_footer(text="Wordle • Bot made by 3_n#7069 • send ""exit"" to terminate the game")
        await ctx.send(embed=embed)
        guessStatus = [0, 0, 0, 0, 0] # 0 = Letter does not exist, 1 = Correct letter, wrong position, 2 = Correct letter and correct position
        try:
            for guessCount in range(5):
                while True:
                    guess = await self.bot.wait_for("message", check = lambda message: message.author == ctx.author, timeout= 300.0)
                    guess_lower = guess.content.lower()
                    if len(guess_lower) == 5:
                        try:
                            for i in range(5):
                                if not(guess_lower[i] in string.ascii_lowercase):
                                    raise IOError
                            break
                        except:
                            embed=discord.Embed(title="Error occured while processing your input.", color=0xff0000)
                            embed.add_field(name="Please check that there are no spaces or special character in your input.", value="If you believe this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).", inline=False)
                            embed.set_footer(text="Wordle • send ""exit"" to terminate the game • Bot made by 3_n#7069")
                            await ctx.send(embed=embed)         
                    elif guess.content == "exit":
                        embed=discord.Embed(title="Wordle results", color=0xffff00)
                        embed.add_field(name="The game is manually terminated.", value=f"The wordle answer is `{answer}`", inline=False)
                        embed.set_footer(text="Wordle • Bot made by 3_n#7069 • results")
                        await ctx.send(embed=embed)
                        return
                    else:
                        embed=discord.Embed(title="Error occured while processing your input.", color=0xff0000)
                        embed.add_field(name="Please check if you inputted a 5-letter word.", value="If you believe this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).", inline=False)
                        embed.set_footer(text="Wordle • send ""exit"" to terminate the game • Bot made by 3_n#7069")
                        await ctx.send(embed=embed)   
                # check whether the inputted word is valid (but doesn't check if the word exists or not, in fact the bot won't even bother checking it!)
                for i in range(5):
                    if guess_lower[i] == answer[i]:
                        guessStatus[i] = 2
                        answer2[i] = "" #removes correct guess
                    elif guess_lower[i] in answer2: #yellow check
                        guessStatus[i] = 1
                    else: #red check
                        guessStatus[i] = 0

                guessEmoji = ""
                guessPlain = ""
                for i in range(5):
                    if guessStatus[i] == 2:
                        guessEmoji += "🟩"
                        guessPlain += "G"
                    elif guessStatus[i] == 1:
                        guessEmoji += "🟨"
                        guessPlain += "Y"
                    else:
                        guessEmoji += "🟥"
                        guessPlain += "R"
                
                embed = discord.Embed(title = f"You guessed `{guess_lower}`.")
                embed.add_field(name="Status:", value=guessEmoji, inline=False)
                embed.add_field(name="Status (If emoji fails to work): ", value=guessPlain, inline=False)
                embed.add_field(name="Legend:", value="🟩/G: Correct letter, correct place\n🟨/Y: Correct letter, wrong place\n🟥/R: Wrong letter", inline=False)
                embed.add_field(name="Number of guesses left", value = str(4 - guessCount), inline = False)
                embed.set_footer(text="Wordle • send ""exit"" to terminate the game • Bot made by 3_n#7069")
                await ctx.send(embed = embed)
                if guessStatus == [2, 2, 2, 2, 2]:
                    correct = True
                    break
                else:
                    continue
            if correct:
                embed=discord.Embed(title="Wordle results", color=0x00ff00)
                embed.add_field(name="Congrats! You have guessed the word correctly.", value=f"The wordle answer is `{answer}`", inline=False)
                embed.set_footer(text="Wordle • Bot made by 3_n#7069 • results")
                await ctx.send(embed=embed) 
            else:
                embed=discord.Embed(title="Wordle results", color=0xffff00)
                embed.add_field(name="Aww, you used up all your guesses. :(", value=f"The wordle answer is `{answer}`", inline=False)
                embed.set_footer(text="Wordle • Bot made by 3_n#7069 • results")
                await ctx.send(embed=embed)
        except asyncio.TimeoutError:
            embed=discord.Embed(title="Wordle results", color=0xffff00)
            embed.add_field(name="The game is terminated due to inactivity.", value=f"The wordle answer is `{answer}`", inline=False)
            embed.set_footer(text="Wordle • Bot made by 3_n#7069 • results")
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(games(bot))