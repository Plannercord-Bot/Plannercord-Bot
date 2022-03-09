import discord
from discord.ext import commands
import os
from decouple import config


# Import secret bot_token, exit if not configured properly
try:
    bot_token = config('bot_token')
except:
    try:
        bot_token = os.environ['bot_token']
    except:
        print("Configure bot token variable first")
        quit()

# Initialize boy
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=";",intents=intents)

# Import cogs from cogs folder
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')
      
#async def command_name(ctx) - no parameters
#async def command_name(ctx, arg) - one parameters
#async def command_name(ctx, arg1, arg2) - two parameters
#async def command_name(ctx, *) - variable parameters



bot.run(bot_token)

