import discord
from discord.ext import commands
import music
import games
import json
from difflib import get_close_matches
import os
import random

cogs = [music, games]
myid = int(os.getenv('OWNER'))
bot = commands.Bot(command_prefix='k!')
bot.remove_command('help')
directory = os.getcwd()

helpText = json.loads(open(f"{directory}/commands/helpText.json").read())
COMMANDS_MUSIC = json.loads(open(f"{directory}/commands/commands_music.json").read())
COMMANDS_GAMES = json.loads(open(f"{directory}/commands/commands_games.json").read())

COMMANDS = [*COMMANDS_MUSIC, *COMMANDS_GAMES]
comString_music = ''
comString_games = ''

for i in COMMANDS_MUSIC:
    comString_music += (i + '\n')
for i in COMMANDS_GAMES:
    comString_games += (i + '\n')

for i in range(len(cogs)):
    cogs[i].setup(bot)

@bot.event
async def on_ready():
    await bot.change_presence(status = discord.Status.idle, activity = discord.Activity(type=discord.ActivityType.listening, name="random songs"))
    print("Bot ready!")

@bot.command()
async def shutdown(ctx):
    # print(ctx.message.author.id)
    if ctx.message.author.id == myid:
        await ctx.send("Shutting down... Check console!")
        await bot.close()
        print("Logged out!")
    else:
        await ctx.send("Access Denied!")

@bot.command()
async def help(ctx, command = None):
    global comString
    if command == None:
        embed = discord.Embed(title="**Help Panel**", description="Here are a list of commands of the bot has!\n\nUse `k!help [command]` to get detailed info about a specific command.", color = 0x11f1f5)
        embed.add_field(name="Music-related", value=comString_music, inline=True)
        embed.add_field(name="Games", value = comString_games, inline = True)
        embed.add_field(name="Others", value="help \n shutdown \n about", inline=True)
        embed.set_footer(text="Bot made by 3_n#7069")
        await ctx.send(embed=embed)
    else:
        try:
            i = 0
            embed = discord.Embed(title="**Help Panel**", describtion = "{0}".format(command), color=0x11f1f5)
            commandDetails = helpText[command]
            commandHeading = ["Attributes", "Aliases", "Description", "Examples"]
            inlineBool = (i % 2 == 0)
            for i in range(4):
                embed.add_field(name = f"{commandHeading[i]}", value = f"{commandDetails[i]}", inline = not inlineBool)
            await ctx.send(embed = embed)
        except:
            potentialCommand = get_close_matches(command, COMMANDS)
            potential = ""
            for i in potentialCommand:
                potential += (i + ", ")
            if potential != "":
                await ctx.send(f"Command not found. Did you mean: `{potential[:-2]}`? Check for all commands with `k!help`.")
            else:
                await ctx.send("Command not found. Check for all commands with `k!help`.")

@bot.command()
async def about(ctx):
    embed=discord.Embed(title="About Page", description="MusicBot written by 3_n with ❤️", color=0x00f552)
    embed.set_thumbnail(url="https://i.ibb.co/kMqz961/ralsei.jpg")
    embed.add_field(name="Special Thanks", value="Alex\nLeo\nSummer\nEugene\n - for helping me test the bot and brainstorm ideas\n\nなみ\n - for giving me motivation and support and being the best, most considerate girlfriend I could ever ask for\n", inline=False)
    embed.add_field(name="Issues & Suggestions", value="Please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).", inline=False)
    embed.set_footer(text="Bot made by 3_n#7069")
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    errorID = ''
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use `k!help` for a list of commands. You can also use `k!help [command]` to look up to a specific command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Some arguments are missing. Please check if you have inputted all required arguments.")
    else:
        k = 0
        for k in range(6):
            errorID += str(random.choice(range(10)))
        await ctx.send(f"An error has occured while executing a command. Please follow this REFID to the owner if you believe this is a bug: `{errorID}`")
        print(f'{errorID}: {error}')

bot.run(os.getenv('TOKEN'))