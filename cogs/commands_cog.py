import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import os
from decouple import config
from db_func import *

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


"""

System Listeners
- Passive functions for debug and CommandNotFound handling

"""


class SystemListeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Plannercord online')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f'{member} has joined a server.')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        print(f'{member} has left the server.')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send('{}, that command does not exist.'.format(
                ctx.author.mention))


"""
Server Commands
- only administrator can use these commands

"""


# Commands that the server administrator can only use
class ServerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Commands

      
    ## Register Command to register a server and create a db collection (sub-db) for it
    @commands.command(
        help=
        "Register the discord server to create a database collection for the server",  #shows when ;help [command] called
        brief="Registeration for data management"  #shows when ;help is called 
    )
    async def server_register(self, ctx, *args):
        # Only accept if author is administrator
        if(ctx.author.guild_permissions.administrator != True):
            await ctx.send(f"You do not have permissions to use that command.")
            return
          
        # Only accept if command has no arguments
        if (len(args) > 0):
            await ctx.send(f"Arguments not needed for that command")
            return
          
        # Call function from db_func with argument ctx.guild object containing different guild/server attributes
        server_data = make_server_collection(ctx.guild)
        message = ""
      
        # Check if server_data is already registered (stored in first element in return value)
        if server_data[0]:
            message = (
                "{} is already registered with timestamp {}."
                "\nIt already has its own collection in the database.".format(
                    ctx.guild.name, server_data[1]))
        else:
            message = "{} server successfully Registered! It now has its own collection in the database.".format(
                ctx.guild.name)

        await ctx.channel.send(message)  #bot reply

      
    ## Meta Command -for debugging only; for checking some important server attributes, as well as members
    @commands.command(
        help=
        "Returns important metadata for database attributes",  #shows when ;help [command] called
        brief="Returns important metadata"  #shows when ;help is called 
    )
    async def meta(self, ctx, *args):
        # Only accept if author is administrator
        if(ctx.author.guild_permissions.administrator != True):
            await ctx.send(f"You do not have permissions to use that command.")
            return
          
        if (len(args) == 0):
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
                                "Roles: {}\n\n".format(guildID, i.id, 
                                                       i.name,
                                                       i.display_name,
                                                       i.discriminator,
                                                       [j.id
                                                        for j in i.roles]))
            await ctx.send(message)  #bot reply

        elif (len(args) > 1):
            await ctx.send(f"Too many arguments")
            return

        if (args[0] == "Guild"):
            print(ctx.guild.id)
            await ctx.send(f"Guild ID: {ctx.guild.id}")

        elif (args[0] == "UserID"):
            print(ctx.author.id)
            await ctx.send(f"User ID: {ctx.author.id}")

        elif (args[0] == "Username"):
            print(ctx.author.name)
            await ctx.send(f"Username: {ctx.author.name}")

        elif (args[0] == "DisplayName"):
            print(ctx.author.display_name)
            await ctx.send(f"Display Name: {ctx.author.display_name}")

        elif (args[0] == "Discriminator"):
            print(ctx.author.discriminator)
            await ctx.send(f"Discriminator: {ctx.author.discriminator}")

        elif (args[0] == "Roles"):
            print([i.id for i in ctx.author.roles])
            await ctx.send(f"Roles: {[i.id for i in ctx.author.roles]}")

        else:
            await ctx.send("Argument not valid")

          
    ## Timezone Command - for changing the discord server-specific timezone (for date and time)
    @commands.command(
        help=
        "Change the timezone of the server.",  #shows when ;help [command] called
        brief=
        "Change the timezone of the server. ;timezone <hours>"  #shows when ;help is called 
    )
    async def timezone(self, ctx, *args):
        # Only accept if author is administrator
        if(ctx.author.guild_permissions.administrator != True):
            await ctx.send(f"You do not have permissions to use that command.")
            return
          
        if (len(args) < 1 or len(args) > 1):
            message = "Too many arguments" if len(
                args) > 1 else "Argument <hours> needed to change timezone"
            await ctx.send(message)
            return
        try:
            timeoffset = int(args[0])
        except:
            await ctx.channel.send("Argument not valid")  #bot reply
            return

        # Call function from db_func with ctx.guild and timeoffset input as arguments
        set_timezone(ctx.guild, timeoffset)
        await ctx.channel.send(
            "Timezone offset successfully changed to {} hours!".format(
                timeoffset))  #bot reply


"""

Test Commands
- prototype commands for testing

"""


class TestCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Commands

    ## Ping Command
    @commands.command(
        help="Play ping-pong with me",  #shows when ;help [command] called
        brief="Prints pong"  #shows when ;help is called 
    )
    async def ping(self, ctx, *args):
        if (len(args) > 0):
            await ctx.send(f"Arguments not needed for that command")
            return
        await ctx.channel.send("pong")  #bot reply

    ## Hi Command
    @commands.command(
        help="Hello!",  #shows when ;help [command] called
        brief="Say hi to me!"  #shows when ;help is called
    )
    async def hi(self, ctx, *args):
        if (len(args) > 0):
            await ctx.send(f"Arguments not needed for that command")
            return
        await ctx.send(f"hello, {ctx.author.mention}")

    ## Hello Command
    @commands.command(
        help=
        "Tag the person you want to say hello to",  #shows when ;help [command] called
        brief="Say hello to someone!"  #shows when ;help is called
    )
    async def hello(self, ctx, *users):
        print(users)
        if (len(users) == 0):
            await ctx.send(f"Arguments needed for that command")
            return

        else:
            greetUsers = ""
            memberIDs = [str(i.id) for i in ctx.guild.members]
            members = [str(i.name) for i in ctx.guild.members]
            for user in users:
                if (user[3:-1] in memberIDs):
                    greetUsers += "{} ".format(
                        ctx.guild.members[memberIDs.index(user[3:-1])].mention)

                elif (user in members):
                    greetUsers += "{} ".format(
                        ctx.guild.members[members.index(user)].mention)
                else:
                    await ctx.send(
                        f"{user} is not a member of the server. Try checking your spelling or capitalization."
                    )

            if greetUsers != "":
                await ctx.send("Hello, " + greetUsers + "!"
                               )  #bot reply if correct parameters

    ## Say Command
    @commands.command(
        help=
        "Repeats any message you send with this command",  #shows when ;help [command] called
        brief="Repeats what you say"  #shows when ;help is called
    )
    async def say(self, ctx, *args):
        response = ""
        if len(args) == 0:
            await ctx.channel.send("You did not write anything")
            return
        for arg in args:  #iterate through all parameters given
            response = response + " " + arg
        await ctx.channel.send(response)

    ## DBsend Command
    @commands.command(
        help=
        "Test command for database communication",  #shows when ;help [command] called
        brief="Test command for db comm"  #shows when ;help is called
    )
    async def dbsend(self, ctx, *message):
        if (len(message) == 0):
            await ctx.send(f"Arguments needed for that command")
            return
        elif (len(message) > 1):
            await ctx.send(f"Too many arguments")
            return
        print(type(message[0]))
        await ctx.send('{} has entered data \"{}\" into the database'.format(
            ctx.author.mention, message[0]))
        collection.insert_one({"_id": message[0]})


"""

CreateCommands
- commands to enter agenda into the database

"""


class CreateCommands(commands.Cog):
    """
    Metadata needed:

    !Important
    Agenda name
    ctx.author
    ctx.author.roles
    datetime made

    !optional
    Description
    Deadline
    Person responsible(assigned to)
    
    """
    def __init__(self, bot):
        self.bot = bot

    #Commands

    ## Add Task Command
    @commands.command(
        help=
        "Create a task and store it in the database",  #shows when ;help [command] called
        brief="Create a task"  #shows when ;help is called 
    )
    async def addtask(self, ctx, *args):
        string = " ".join(args)
        print(string)
        if (len(args) < 1):
            await ctx.send(f"Missing/Incomplete arguments.")
            return
        taskName = args[0]

        message = ""
        await ctx.channel.send(message)  #bot reply

    ## Metadata Command
    @commands.command(
        help=
        "Returns important metadata for database attributes",  #shows when ;help [command] called
        brief="Returns important metadata"  #shows when ;help is called 
    )
    async def metadata(self, ctx, *args):
        if (len(args) == 0):
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
                                "Roles: {}\n\n".format(guildID, i.id, i.name,
                                                       i.display_name,
                                                       i.discriminator,
                                                       [j.id
                                                        for j in i.roles]))
            await ctx.send(message)  #bot reply
        elif (len(args) > 1):
            await ctx.send(f"Too many arguments")
            return

        if (args[0] == "Guild"):
            await ctx.send(f"Guild ID: {ctx.guild.id}")

        elif (args[0] == "UserID"):
            await ctx.send(f"User ID: {ctx.author.id}")

        elif (args[0] == "Username"):
            await ctx.send(f"Username: {ctx.author.name}")

        elif (args[0] == "DisplayName"):
            await ctx.send(f"Display Name: {ctx.author.display_name}")

        elif (args[0] == "Discriminator"):
            await ctx.send(f"Discriminator: {ctx.author.discriminator}")

        elif (args[0] == "Roles"):
            await ctx.send(f"Roles: {[i.id for i in ctx.author.roles]}")

        else:
            await ctx.send("Argument not valid")


# Add the command group classes
def setup(bot):
    bot.add_cog(SystemListeners(bot))
    bot.add_cog(ServerCommands(bot))
    bot.add_cog(TestCommands(bot))
    bot.add_cog(CreateCommands(bot))
