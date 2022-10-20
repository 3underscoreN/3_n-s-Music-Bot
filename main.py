import disnake
from disnake.ext import commands as disnakeCommands
import music
import games
import json
from difflib import get_close_matches
import os
import random
import logging
import itertools

errorID = 0
logging.basicConfig(
    filename = "botLog.log", 
    level = logging.INFO, 
    format = "%(asctime)s %(levelname)s: %(message)s", 
    datefmt = '%m/%d/%Y %I:%M:%S %p'
)

intents = disnake.Intents.default()
intents.members = True
intents.message_content = True

cogs = [music, games]
myid = int(os.getenv('OWNER'))
bot = disnakeCommands.Bot(
    command_prefix='k!', 
    intents = intents,
    sync_commmands_debug = True
)

# help command related
bot.remove_command('help')
COMMANDS = json.loads(open("./commands/commands.json").read())
COMMANDS_INFO = json.loads(open("./commands/commandsInfo.json").read())
COMMANDS_INFO_HEADING = ["format", "aliases", "description", "examples"]
commands_unordered = list(itertools.chain.from_iterable(COMMANDS.values()))

for i in range(len(cogs)):
    cogs[i].setup(bot)

@bot.event
async def on_ready():
    await bot.change_presence(status = disnake.Status.idle, activity = disnake.Activity(type=disnake.ActivityType.listening, name="random songs"))
    print("Bot ready!")

@bot.command()
async def shutdown(ctx):
    if ctx.message.author.id == myid:
        embed = disnake.Embed(title = "Success", color = 0x00ff00)
        embed.add_field(name = "Bot shutting down...", value = "Check terminal!")
        embed.set_footer(text = "Shutdown • Bot made by 3_n#7069")
        await ctx.send(embed = embed)
        await bot.close()
    else:
        raise disnakeCommands.NotOwner()

#ping
@bot.command()
async def ping(ctx):
    embed = disnake.Embed(title = "Pong!", color = 0x11f1f5)
    embed.add_field(name=f"The bot's latency is `{round(bot.latency * 1000, 1)}ms`", value = "If there's a noticable delay in command processing, the bot might have an internal error.\nPlease get in touch with 3_n#7069 if that happens.", inline=False)
    embed.set_footer(text = "Ping • Bot made by 3_n#7069")
    await ctx.send(embed = embed)

# debug only
@bot.command()
async def raiseException(ctx):
    if ctx.message.author.id == myid:
        raise Exception("This exception is raised for debugging purpose. No action is required.")
    else:
        raise disnakeCommands.NotOwner()

@bot.command()
async def help(ctx, command = None):
    if command == None or command == "None":
        embed = disnake.Embed(title="**Help Panel**", description="Here is a list of commands the bot has!\n\nUse `k!help [command]` to get detailed info about a specific command.", color = 0x11f1f5)
        for i in COMMANDS.keys():
            embed.add_field(name = i.capitalize(), value = "\n".join(COMMANDS[i]), inline = True)
        embed.set_footer(text="Bot made by 3_n#7069")
        await ctx.send(embed = embed)
    else:
        try:
            embed = disnake.Embed(title="**Help Panel**", description = "{0}".format(command), color=0x11f1f5)
            tDetails = COMMANDS_INFO[command.lower()] # temp, can be discarded
            for i in COMMANDS_INFO_HEADING:
                if type(tDetails[i]) != type([]):
                    embed.add_field(name = i.capitalize(), value = f"`{tDetails[i]}`" if i == "format" else tDetails[i], inline = False)
                else:
                    embed.add_field(name = i.capitalize(), value = ", ".join(tDetails[i]) if i == "aliases" else "`" + "`\n`".join(tDetails[i]) + "`", inline = False)
            await ctx.send(embed = embed)
        except KeyError: # command not found
            potentialCommand = get_close_matches(command, commands_unordered)
            potential = ""
            for i in potentialCommand:
                potential += f"{i}, "
            if potential != "":
                embed = disnake.Embed(title = "Error: Command not found", color = 0xff0000)
                embed.add_field(name = f"The command you entered is not found.", value = f"Do you mean: `{potential[:-2]}`?\nCheck all commands available with `k!help`.\nIf you believe this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).")
                embed.set_footer(text = "Bot made by 3_n#7069")
                await ctx.send(embed = embed)
            else:
                embed = disnake.Embed(title = "Error: Command not found", color = 0xff0000)
                embed.add_field(name = "The command you entered is not found.", value = "Check all commands available with `k!help`.\nIf you believe this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).")
                embed.set_footer(text = "Bot made by 3_n#7069")
                await ctx.send(embed = embed)

#about
@bot.command(aliases = ["abt"])
async def about(ctx):
    embed = disnake.Embed(title="About Page", description="MusicBot written by 3_n with ❤️", color=0x00f552)
    embed.set_thumbnail(url="https://i.ibb.co/kMqz961/ralsei.jpg")
    embed.add_field(name="Special Thanks", value="Alex (Alice the horny), Leo (can't come up with nickname for this person), Summer (我就是遜啦),\nEugene (Paramount but not)\n - for helping me test the bot and brainstorming ideas\n\n", inline=False)
    embed.add_field(name="Issues & Suggestions", value="Please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).", inline=False)
    embed.set_footer(text="Bot made by 3_n#7069")
    await ctx.send(embed = embed)

#Error handling
@bot.event
async def on_command_error(ctx, error):
    errorID = ''
    if isinstance(error, disnakeCommands.CommandNotFound):
        embed=disnake.Embed(title="Error: Command not found", color=0xff0000)
        embed.add_field(name="The command you entered does not seem to be valid.", value="Please double-check your entry. If you don't know what you are doing, you can use `k!help` for a list of disnakeCommands availabe.\n\nYou can also use `k!help [command]` to find details about a specific command.\nIf you believe this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).", inline=False)
        embed.set_footer(text="Bot made by 3_n#7069")
        await ctx.send(embed=embed)

    if isinstance(error, disnakeCommands.UserInputError):
        embed = disnake.Embed(title = "Error: User Input Error", color = 0xff0000)
        embed.add_field(name = "We have detected an error in your input.", value = "Please check your parameters to see if they are in the right formation or are entered correctly.\nIf you believe this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).")
        embed.set_footer(text="Bot made by 3_n#7069")
        await ctx.send(embed = embed)

    if isinstance(error, disnakeCommands.MissingRequiredArgument):
        embed=disnake.Embed(title="Error: Missing arguments", color=0xff0000)
        embed.add_field(name="Some required arguments in your entry seems to be missing.", value="Please double-check your entry. You can use `k!help [command]` to find all the required arguments (usually bracketed by `<>`) in the command.\nIf you believe this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).", inline=False)
        embed.set_footer(text="Bot made by 3_n#7069")
        await ctx.send(embed=embed)

    if isinstance(error, disnakeCommands.TooManyArguments):
        embed=disnake.Embed(title="Error: Too many arguments", color=0xff0000)
        embed.add_field(name="You have entered too many arguments in your command.", value="Please double-check your entry. You can use `k!help [command]` to find the arguments that are redundant in your command.\nIf you believe this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).", inline=False)
        embed.set_footer(text="Bot made by 3_n#7069")
        await ctx.send(embed=embed)

    if isinstance(error, disnakeCommands.NotOwner):
        embed=disnake.Embed(title="Error: Access Denied", color=0xff0000)
        embed.add_field(name="It seems like only the owner can execute the command.", value="Please double-check your entry. If you believe this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).", inline=False)
        embed.set_footer(text="Bot made by 3_n#7069")
        await ctx.send(embed=embed)

    if isinstance(error, disnakeCommands.BotMissingPermissions):
        embed=disnake.Embed(title="Error: Bot missing permission", color=0xff0000)
        embed.add_field(name="It seems like the bot doesn't have permission to do so", value="Please politely ask moderators to fix this issue. If you believe this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).", inline=False)
        embed.set_footer(text="Bot made by 3_n#7069")
        await ctx.send(embed=embed)

    if isinstance(error, disnakeCommands.NoPrivateMessage):
        embed=disnake.Embed(title="Error: No Direct Message", color=0xff0000)
        embed.add_field(name="This command can't run in direct message.", value="Please run the command in a server text channel. If you believe this is a bug, please open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).", inline=False)
        embed.set_footer(text="Bot made by 3_n#7069")
        await ctx.send(embed=embed)

    if isinstance(error, music.ExceptionResolved):
        logging.warning(f"Exception reported from music cog, handled. Original Message: {repr(error)}") # This is a custom exception that is raised when the bot is unable to resolve the song. It is handled in the music cog.

    if isinstance(error, disnakeCommands.CommandInvokeError):
        for _ in range(6):
            errorID += str(random.choice(range(10)))
        embed=disnake.Embed(title="Error: Unexpected error", color=0xff0000)
        embed.add_field(name="There is an unexpected error while executing your command.", value=f"If you believe this is a bug, please forward this error ID (`{errorID}`) to 3_n#7069 or open an issue on [Github project page](https://github.com/3underscoreN/3_n-s-Music-Bot).", inline=False)
        embed.set_footer(text="Bot made by 3_n#7069")
        await ctx.send(embed = embed)
    if errorID == '':
        logging.warning(f"Expection caught ({type(error)}, resolved). Original Message: {repr(error)}")
    else:
        logging.error(f"Exception reported and uncaught with ID {errorID}: {repr(error)}")

if __name__ == "__main__":
    bot.run(os.getenv('TOKEN'))