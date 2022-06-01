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
        print(f"{answer} generated")
        guessCount = 0
        correct = False
        await ctx.send("The word has been generated. Start guessing by typing a 5-letter word! Note that if no input is detected for 300 seconds, the bot timeouts.\nIf you want to terminate the game manually, enter `exit`.")
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
                            await ctx.send("Error has been detected in your input. Please check your input. If you believe this is an error, please contect `3_n#7069`.If you want to terminate the game manually, enter `exit`.")         
                    elif guess.content == "exit":
                        await ctx.send(f"Game has ended due to manual termination. The word is: `{answer}`.")
                        return
                    else:
                        await ctx.send("Please enter a 5-letter word!\nIf you want to terminate the game manually, enter `exit`.")
                # check whether the inputted word is valid (but doesn't check if the word exists or not, in fact the bot won't even bother checking it!)
                for i in range(5):
                    if guessStatus[i] != 2:
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
                embed.set_footer(text="Wordle • Bot made by 3_n#7069")
                await ctx.send(embed = embed)
                if guessStatus == [2, 2, 2, 2, 2]:
                    correct = True
                    break
                else:
                    await ctx.send("If you want to terminate the game manually, enter `-1`.")
                    continue
            if correct:
                await ctx.send(f"Congrats! You have guessed the word `{answer}` correctly!")
            else:
                await ctx.send(f"Too bad, you used up all your guesses. The correct word is {answer}.")
        except asyncio.TimeoutError:
            await ctx.send(f"As no input is detected, the wordle game has ended. The answer is: `{answer.lower()}`")

def setup(bot):
    bot.add_cog(games(bot))