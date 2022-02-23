import discord
from discord.ext import commands
import os

bot_token = os.environ['bot_token']

bot = commands.Bot(command_prefix=";")

#async def command_name(ctx) - no parameters
#async def command_name(ctx, arg) - one parameters
#async def command_name(ctx, arg1, arg2) - two parameters
#async def command_name(ctx, *) - variable parameters

@bot.command(
  help = "Play ping-pong with me", #shows when ;help [command] called
  brief = "Prints pong" #shows when ;help is called 
)
async def ping(ctx):
	await ctx.channel.send("pong") #bot reply

@bot.command()
async def hello(ctx, *, user: discord.Member = None):
    if user:
        await ctx.send(f"hello, {user.mention}") #bot reply if correct parameters
    else:
        await ctx.send('You have to say who do you want to say hello to') #bot reply if wrong/incomplete parameters

@bot.command()
async def say(ctx, *args):
    response = ""
    for arg in args: #iterate through all parameters given
        response = response + " " + arg
    await ctx.channel.send(response)

bot.run(bot_token)