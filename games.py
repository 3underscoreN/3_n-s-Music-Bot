import discord
from discord.ext import commands
import asyncio
import random
import json, os
import asyncio
import string

directory = os.getcwd()

wordList = json.loads(open(f"{directory}/games/wordle.json").read())

class noFriendsDetected(Exception):
    pass

class botDetected(Exception):
    pass

class TicTacToeClass():
    def __init__(self, player1, player2):
        self.board = [[None, None, None], [None, None, None], [None, None, None]]
        self.player1 = [player1, ":o:"]
        if player2 == "Computer":
            self.player2 = [None, ":x:"]
        else:
            self.player2 = [player2, ":x:"]
        self.playerList = [self.player1, self.player2]
        self.firstPlayer = random.choice(self.playerList)
        self.currentplayer = self.firstPlayer[0]
        self.rotation = self.playerList.index(self.firstPlayer)
        self.iteration = 0

    def fetchPlayer(self, player):
        if player in self.player1:
            return self.player1
        else:
            return self.player2

    def checkwin(self, player):
        self.playerToCheck = self.fetchPlayer(player)
        #row check
        for row in self.board:
            if len(set(row)) == 1 and row[0] == self.playerToCheck[1]:
                return True
        #column check
        for column in range(3):
            if self.board[0][column] == self.board[1][column] and self.board[1][column] == self.board[2][column]:
                if self.board[0][column] == self.playerToCheck[1]:
                    return True
        #diag check
        if (self.board[0][0] == self.board[1][1] and self.board[1][1] == self.board[2][2]) or (self.board[0][2] == self.board[1][1] and self.board[1][1] == self.board[2][0]):
            if self.board[1][1] == self.playerToCheck[1]:
                return True
        return False

    def entry(self, RowPos, ColumnPos, player):
        self.playerToEnter = self.fetchPlayer(player)

        if self.board[RowPos][ColumnPos] is None:
                self.board[RowPos][ColumnPos] = self.playerToEnter[1]
                self.iteration += 1
        else:
            raise Exception
        if self.iteration == 9:
            return -1
        if self.checkwin(self.playerToEnter[0]):
            return player
        else:
            self.rotation = (self.rotation + 1) % 2
            return self.playerList[self.rotation][0]
    
class games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
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

    @commands.command(aliases = ["ttt"])
    @commands.guild_only()
    async def tictactoe(self, ctx, player:discord.Member):
        player1 = ctx.author
        player2 = player
        TicTacToe = TicTacToeClass(player1, player2)
        currentPlayer = TicTacToe.currentplayer
        try:
            if player1 == player2:
                raise noFriendsDetected("You should find someone to play tic-tac-toe with!")
            elif player.bot:
                raise botDetected("You can't play with a bot!")
            while not(TicTacToe.checkwin(currentPlayer)):
                embed = discord.Embed(title = "Tic-Tac-Toe", color = 0x00fffb)
                board = ''
                for row in range(3):
                    for column in range(3):
                        if TicTacToe.board[row][column] is None:
                            board += ':free:'
                        else:
                            board += TicTacToe.board[row][column]
                    board += '\n'
                embed.add_field(name = "Board", value = f"{board}", inline = False)
                if currentPlayer is None: 
                    embed.add_field(name = f"It is computer's turn! ", value = "Please wait for a bit.", inline = False)
                else:
                    embed.add_field(name = f"It is @{currentPlayer}'s turn! ", value = "Please play by entering a non-occupied box (1-9, where 1 is the top left and 2 is the top middle and so on).\nIf no input is detected in 120 seconds, the game will be terminated.\nYou can also terminate the game when it's your turn to play by entering `exit`.", inline = False)
                embed.set_footer(text = "Tic-Tac-Toe • Bot made by 3_n#7069")
                await ctx.send(embed = embed)
                if currentPlayer != None:
                    while True:
                        playerInput = await self.bot.wait_for("message", check = lambda message: message.author == currentPlayer, timeout= 120.0)
                        if playerInput.content == "exit":
                            raise IOError
                        try:
                            num = int(playerInput.content)
                            if num in range(1, 10):
                                rawInput = [(num - 1) // 3, (num - 1) % 3]
                                break
                            else:
                                raise Exception
                        except:
                            embed=discord.Embed(title="Error occured while processing your input.", color=0xff0000)
                            embed.add_field(name="Please check that the number you entered is an integer between 1 and 9", value="If you believe this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).", inline=False)
                            embed.set_footer(text="Tic-Tac-Toe • Bot made by 3_n#7069")
                            await ctx.send(embed = embed)
                    currentPlayer = TicTacToe.entry(rawInput[0], rawInput[1], currentPlayer)
                else:
                    await ctx.send("Computer is thinking...")
                    currentPlayer = TicTacToe.compEntry()
                if currentPlayer == -1:
                    break
            embed = discord.Embed(title = "Tic-Tac-Toe results", color = 0x00fffb)
            board = ''
            for row in range(3):
                for column in range(3):
                    if TicTacToe.board[row][column] is None:
                        board += ':free:'
                    else:
                        board += TicTacToe.board[row][column]
                board += '\n'
            embed.add_field(name = "Board", value = f"{board}", inline = False)
            if currentPlayer == -1:
                embed.add_field(name = "Draw", value = "The game has ended in a draw, like most other game does.", inline = False)
            else:
                if currentPlayer is None: 
                    mention = "Computer"
                else:
                    mention = f"@{currentPlayer}"
                embed.add_field(name = f"{mention} wins!", value = "This game has ended and all the honor goes to them!", inline = False)
            embed.set_footer(text = "Tic-Tac-Toe results • Bot made by 3_n#7069")
            await ctx.send(embed = embed)
        except asyncio.TimeoutError:
            embed=discord.Embed(title="Tic-Tac-Toe results", color=0xffff00)
            embed.add_field(name="Terminated", value="The game is terminated due to inactivity.", inline=False)
            embed.set_footer(text="Tic-Tac-Toe • Bot made by 3_n#7069 • results")
            await ctx.send(embed = embed)
        except IOError:
            embed=discord.Embed(title="Tic-Tac-Toe results", color=0xffff00)
            embed.add_field(name="Terminated", value="The game is terminated due to manual termination.", inline=False)
            embed.set_footer(text="Tic-Tac-Toe • Bot made by 3_n#7069 • results")
            await ctx.send(embed = embed)
        except noFriendsDetected:
            embed=discord.Embed(title="Error: No friends detected", color=0xff0000)
            embed.add_field(name="You are trying to play tic-tac-toe with yourself?", value="You should find someone to play with. :)", inline=False)
            embed.set_footer(text="Bot made by 3_n#7069")
            await ctx.send(embed = embed)
        except botDetected:
            embed=discord.Embed(title="Error: Bot detected", color=0xff0000)
            embed.add_field(name="You are trying to play tic-tac-toe with a bot?", value="Bots might not be clever enough to play the game. Find a real person!", inline=False)
            embed.set_footer(text="Bot made by 3_n#7069")
            await ctx.send(embed = embed)
       
def setup(bot):
    bot.add_cog(games(bot))