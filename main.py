import discord
from discord.ext import commands
import music
import games
import json
from difflib import get_close_matches
import os

cogs = [music, games]
myid = 376343682644836353
bot = commands.Bot(command_prefix='k!')
bot.remove_command('help')
directory = os.getcwd()

helpText = json.loads(open(f"{directory}/commands/helpText.json").read())
COMMANDS = json.loads(open(f"{directory}/commands/commands.json").read())
comString = ''

for i in COMMANDS:
    comString += (i + '\n')


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
        embed.add_field(name="Music-related", value=comString, inline=True)
        embed.add_field(name="Others", value="help \n shutdown", inline=True)
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

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use `k!help` for a list of commands. You can also use `k!help [command] to look up to a specific command.")

bot.run('ODk2MDA3NTcxMDU4NjEwMjA3.GUHAMo.iqp3vCd5_jD6tN1cif-t8kxf3668NgSe5tu6Go')