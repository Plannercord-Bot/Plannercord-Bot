import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import os
from decouple import config
from functions import make_server_collection

# Import secret mongodb_server
try:
    mongodb_server = config('mongodb_server')
except:
    try:
        mongodb_server = os.environ['mongodb_server']
    except:
        print("Configure mongodb server variable first")
        quit()



cluster = MongoClient(mongodb_server)
db = cluster["test"]
collection = db["test_collection"]


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

    ## Register Command
    @commands.command(
      help = "Register the discord server to create a database collection for the server", #shows when ;help [command] called
      brief = "Registeration for data management" #shows when ;help is called 
    )
    async def server_register(self,ctx, *args):
      if(len(args)>0):
        await ctx.send(f"Arguments not needed for that command")
        return
      if make_server_collection(ctx.guild):
        await ctx.channel.send("Server was already registered before and has its own collection in the database.\nIts unique ID is {}".format(ctx.guild.id)) #bot reply
      else:
        await ctx.channel.send("Server successfully Registered! Your server now has its own collection in the database\nwith its unique ID {}".format(ctx.guild.id)) #bot reply


    ## Metadata Command
    @commands.command(
      help = "Returns important metadata for database attributes", #shows when ;help [command] called
      brief = "Returns important metadata" #shows when ;help is called 
    )
    async def meta(self,ctx, *args):
      if(len(args)==0):
        guildID = ctx.guild.id
        message = ""
        for i in ctx.guild.members:
          if i.bot == True:
            pass
          else:
            message += ("Guild ID: {}\n"
                       "User ID: {}\n"
                       "Username: {}\n"
                       "Display Name: {}\n"
                       "Discriminator: {}\n"
                       "Roles: {}\n\n".format(guildID,i.id,i.name,i.display_name,i.discriminator,[j.id for j in i.roles]))
        await ctx.send(message) #bot reply
      elif(len(args)>1):
        await ctx.send(f"Too many arguments")
        return
      
      if(args[0] == "Guild"):
        print(ctx.guild.id)
        await ctx.send(f"Guild ID: {ctx.guild.id}")

      elif(args[0] == "UserID"):
        print(ctx.author.id)
        await ctx.send(f"User ID: {ctx.author.id}")

      elif(args[0] == "Username"):
        print(ctx.author.name)
        await ctx.send(f"Username: {ctx.author.name}")
        
      elif(args[0] == "DisplayName"):
        print(ctx.author.display_name)
        await ctx.send(f"Display Name: {ctx.author.display_name}")

      elif(args[0] == "Discriminator"):
        print(ctx.author.discriminator)
        await ctx.send(f"Discriminator: {ctx.author.discriminator}")

      elif(args[0] == "Roles"):
        print([i.id for i in ctx.author.roles])
        await ctx.send(f"Roles: {[i.id for i in ctx.author.roles]}")
        
      else:
        await ctx.send("Argument not valid")
        
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
    async def hello(self,ctx, *users):
      print(users)
      if(len(users)==0):
        await ctx.send(f"Arguments needed for that command")
        return
      
      else:
        greetUsers = ""
        memberIDs = [str(i.id) for i in ctx.guild.members]
        members = [str(i.name) for i in ctx.guild.members]
        for user in users:
          if(user[3:-1] in memberIDs):
            greetUsers +="{} ".format(ctx.guild.members[memberIDs.index(user[3:-1])].mention)
            
          elif(user in members):
            greetUsers +="{} ".format(ctx.guild.members[members.index(user)].mention)
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
        collection.insert_one({"_id":message[0]})



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