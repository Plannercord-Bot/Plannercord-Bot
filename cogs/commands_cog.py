import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import os


cluster = MongoClient(os.environ['mongodb_server'])
db = cluster["test"]
collection = db["test"]


class SystemListeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Plannercord online')

    @commands.Cog.listener()
    async def on_member_join(self,member):
        print(f'{member} has joined a server.')

    @commands.Cog.listener() 
    async def on_member_remove(self,member):
        print(f'{member} has left the server.')

    @commands.Cog.listener()
    async def on_command_error(self,ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send('{}, that command does not exist.'.format(ctx.author.mention))



class TestCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    #Commands

      
    ## Ping Command
    @commands.command(
      help = "Play ping-pong with me", #shows when ;help [command] called
      brief = "Prints pong" #shows when ;help is called 
    )
    async def ping(self,ctx, *args):
      if(len(args)>0):
        await ctx.send(f"Arguments not needed for that command")
        return
      await ctx.channel.send("pong") #bot reply

      
    ## Hi Command
    @commands.command(
      help = "Hello!", #shows when ;help [command] called
      brief = "Say hi to me!" #shows when ;help is called
    )
    async def hi(self,ctx,*args):
      if(len(args)>0):
        await ctx.send(f"Arguments not needed for that command")
        return
      await ctx.send(f"hello, {ctx.author.mention}")

      
    ## Hello Command
    @commands.command(
      help = "Tag the person you want to say hello to", #shows when ;help [command] called
      brief = "Say hello to someone!" #shows when ;help is called
    )
    async def hello(self,ctx, *users: discord.Member):
      if(len(users)==0):
        await ctx.send(f"Arguments needed for that command")
        return
      else:
        greetUsers = ""
        members = [str(i) for i in ctx.guild.members]
        print(members)
        for user in users:
          if(str(user) in members):
            greetUsers +="{} ".format(user.mention)
          else:
            await ctx.send(f"{user} is not a member of the server. Try checking your spelling or capitalization.")
            
        if greetUsers != "":
          await ctx.send("Hello, " + greetUsers + "!") #bot reply if correct parameters

          
    ## Say Command
    @commands.command(
      help = "Repeats any message you send with this command", #shows when ;help [command] called
      brief = "Repeats what you say" #shows when ;help is called
    )
    async def say(self,ctx, *args):
      response = ""
      if len(args)==0:
        await ctx.channel.send("You did not write anything")
        return
      for arg in args: #iterate through all parameters given
          response = response + " " + arg
      await ctx.channel.send(response)

      
    ## DBsend Command
    @commands.command(
      help = "Test command for database communication", #shows when ;help [command] called
      brief = "Test command for db comm" #shows when ;help is called
    )
    async def dbsend(self,ctx, *message):
        if(len(message)==0):
          await ctx.send(f"Arguments needed for that command")
          return
        elif(len(message)>1):
          await ctx.send(f"Too many arguments")
          return
        print(type(message[0]))
        await ctx.send('{} has entered data \"{}\" into the database'.format(ctx.author.mention, message[0]))
        collection.insert_many({"_id":message})



class ExampleCommandGroup1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
      
    @commands.command()
    async def command1(self,ctx, member : discord.Member, area=''):
        if (area != ''):
          await ctx.send('{} has <command> {} on the {}'.format(ctx.author.mention, member.mention, area))
        else:
          await ctx.send('{} has <command> {}'.format(ctx.author.mention, member.mention))

    @commands.command()
    async def command2(self,ctx, member : discord.Member):
          await ctx.send('{} command {}'.format(ctx.author.mention, member.mention))

    @commands.command()
    async def command3(self,ctx, member : discord.Member):
        await ctx.send('{} <command> {}'.format(ctx.author.mention, member.mention))


# Add the command group classes
def setup(bot):
  bot.add_cog(SystemListeners(bot))
  bot.add_cog(TestCommands(bot))
  bot.add_cog(ExampleCommandGroup1(bot))