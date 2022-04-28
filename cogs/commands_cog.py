import argparse
import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import os
from decouple import config
from db_func import *
from datetime import datetime, date, timedelta

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
        await periodic_checker(self.bot)

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
        brief="Registration for data management"  #shows when ;help is called 
    )
    async def server_register(self, ctx, *args):
        # Only accept if author is administrator
        if (ctx.author.guild_permissions.administrator != True):
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
        if (ctx.author.guild_permissions.administrator != True):
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
        if (ctx.author.guild_permissions.administrator != True):
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

    ## Test Reminder Command
    @commands.command(
        help=
        "Test command for reminder testing",  #shows when ;help [command] called
        brief="Test command for reminder"  #shows when ;help is called
    )
    async def testrem(self, ctx, *args):
        await ctx.send("Start")
        await periodic_checker(ctx)

    ## Delete Collection Command
    @commands.command(
        help=
        "Debug command; deletes the guild's collection in the database",  #shows when ;help [command] called
        brief="Delete current discord server data from database"  #shows when ;help is called
    )
    async def clearserver(self, ctx, *args):
        await ctx.send("Test Start")
        await delCollection(ctx)

    ## Test Function Command
    @commands.command(
        help=
        "Debug command, only use when you know what to do",  #shows when ;help [command] called
        brief="Debug command"  #shows when ;help is called
    )
    async def testfunc(self, ctx, *args):
        await ctx.send("Test Start")
        message = personal_summary_agenda(ctx)
        await ctx.send(message)

"""

CreateCommands
- commands to enter agenda into the database

"""


class CreateGroupCommands(commands.Cog):
    """
    Metadata needed:

    !Important
    Agenda name
    ctx.author
    ctx.author.roles
    datetime made

    !Optional
    Description
    Deadline
    Person responsible(assigned to)
    
    """
    def __init__(self, bot):
        self.bot = bot

    #Commands

    ## Add Group Task Command - Boilerplate for add agenda commands
    @commands.command(
        help="Create a group task and store it in the database.\n\n"
        "Format:\n"
        "\t;addtask <task name>;<Date in mm-dd-yy>;<Time in hh:mm> \n\n"
        "Required Arguments:\n"
        "\t<task name>",  #shows when ;help [command] called
        brief="Create a group task"  #shows when ;help is called 
    )
    async def addtask(self, ctx, *args):
        AgendaType = "Task"
        print(len(args))
        if (len(args) < 1):
            await ctx.send(f"Invalid number of Arguments.\n"
                           "The addtask command requires Task Name argument.\n"
                           "Type ;help addtask for more information.")
            return

        # Arguments after command are joined and manually separated using specified delimiter ';'
        string = " ".join(args)
        args = string.split(";")

        i = 0
        while i < len(args):
          print(args)
          if len(args[i])<1:
            args.remove(args[i])
            i = i-1
          i+=1
            
        if (len(args) > 3):
            await ctx.send(f"Invalid number of Arguments.\n"
                           "More arguments than required detected.\n"
                           "Type ;help addtask for more information.")
            return

        message = await add_agenda(ctx, AgendaType, args)

        await ctx.channel.send(message)  #bot reply

    ## Add Group Project Command
    @commands.command(
        help="Create a group project and store it in the database.\n\n"
        "Format:\n"
        "\t;addproj <project name>;<Date in mm-dd-yy>;<Time in hh:mm> \n\n"
        "Required Arguments:\n"
        "\t<project name>",  #shows when ;help [command] called
        brief="Create a group project"  #shows when ;help is called 
    )
    async def addproj(self, ctx, *args):
        AgendaType = "Project"
        if (len(args) < 1):
            await ctx.send(
                f"Invalid number of Arguments.\n"
                "The addproj command requires Project Name argument.\n"
                "Type ;help addproj for more information.")
            return

        # Arguments after command are joined and manually separated using specified delimiter ';'
        string = " ".join(args)
        args = string.split(";")
        i = 0
        while i < len(args):
          print(args)
          if len(args[i])<1:
            args.remove(args[i])
            i = i-1
          i+=1
        if (len(args) > 3):
            await ctx.send(f"Invalid number of Arguments.\n"
                           "More arguments than required detected.\n"
                           "Type ;help addproj for more information.")
            return

        message = await add_agenda(ctx, AgendaType, args)

        await ctx.channel.send(message)  #bot reply

    ## Add Group Meeting Command
    @commands.command(
        help="Create a group meeting and store it in the database.\n\n"
        "Format:\n"
        "\t;addmeet <meeting name>;<Date in mm-dd-yy>;<Time in hh:mm> \n\n"
        "Required Arguments:\n"
        "\t<meeting name>",  #shows when ;help [command] called
        brief="Create a group meeting"  #shows when ;help is called 
    )
    async def addmeet(self, ctx, *args):
        AgendaType = "Meeting"
        if (len(args) < 1):
            await ctx.send(
                f"Invalid number of Arguments.\n"
                "The addmeet command requires Meeting Name argument.\n"
                "Type ;help addmeet for more information.")
            return

        # Arguments after command are joined and manually separated using specified delimiter ';'
        string = " ".join(args)
        args = string.split(";")
        i = 0
        while i < len(args):
          print(args)
          if len(args[i])<1:
            args.remove(args[i])
            i = i-1
          i+=1
        if (len(args) > 3):
            await ctx.send(f"Invalid number of Arguments.\n"
                           "More arguments than required detected.\n"
                           "Type ;help addmeet for more information.")
            return

        message = await add_agenda(ctx, AgendaType, args)

        await ctx.channel.send(message)  #bot reply

    ## Add Group Reminder Command
    @commands.command(
        help="Create a group reminder and store it in the database.\n\n"
        "Format:\n"
        "\t;addrem <reminder name>;<Date in mm-dd-yy>;<Time in hh:mm> \n\n"
        "Required Arguments:\n"
        "\t<reminder name>",  #shows when ;help [command] called
        brief="Create a group reminder"  #shows when ;help is called 
    )
    async def addrem(self, ctx, *args):
        AgendaType = "Reminder"
        if (len(args) < 1):
            await ctx.send(
                f"Invalid number of Arguments.\n"
                "The addrem command requires Reminder Name argument.\n"
                "Type ;help addrem for more information.")
            return

        # Arguments after command are joined and manually separated using specified delimiter ';'
        string = " ".join(args)
        args = string.split(";")
        i = 0
        while i < len(args):
          print(args)
          if len(args[i])<1:
            args.remove(args[i])
            i = i-1
          i+=1
        if (len(args) > 3):
            await ctx.send(f"Invalid number of Arguments.\n"
                           "More arguments than required detected.\n"
                           "Type ;help addrem for more information.")
            return

        message = await add_agenda(ctx, AgendaType, args)

        await ctx.channel.send(message)  #bot reply

class CreatePersonalCommands(commands.Cog):
    """
    Metadata needed:

    !Important
    Agenda name
    ctx.author
    ctx.author.roles
    datetime made

    !Optional
    Description
    Deadline
    Person responsible(assigned to)
    
    """
    def __init__(self, bot):
        self.bot = bot

    #Commands

    ## Add Personal Task Command
    @commands.command(
        help="Create a personal task and store it in the database.\n\n"
        "Format:\n"
        "\t;addmytask <task name>;<Date in mm-dd-yy>;<Time in hh:mm> \n\n"
        "Required Arguments:\n"
        "\t<task name>",  #shows when ;help [command] called
        brief="Create a personal task"  #shows when ;help is called 
    )
    async def addmytask(self, ctx, *args):
        AgendaType = "MyTask"
        print(len(args))
        if (len(args) < 1):
            await ctx.send(f"Invalid number of Arguments.\n"
                           "The addmtask command requires Task Name argument.\n"
                           "Type ;help addmytask for more information.")
            return

        # Arguments after command are joined and manually separated using specified delimiter ';'
        string = " ".join(args)
        args = string.split(";")

        i = 0
        while i < len(args):
          print(args)
          if len(args[i])<1:
            args.remove(args[i])
            i = i-1
          i+=1
            
        if (len(args) > 3):
            await ctx.send(f"Invalid number of Arguments.\n"
                           "More arguments than required detected.\n"
                           "Type ;help addmytask for more information.")
            return

        message = await add_agenda(ctx, AgendaType, args)

        await ctx.channel.send(message)  #bot reply

    ## Add Personal Project Command
    @commands.command(
        help="Create a personal project and store it in the database.\n\n"
        "Format:\n"
        "\t;addmyproj <project name>;<Date in mm-dd-yy>;<Time in hh:mm> \n\n"
        "Required Arguments:\n"
        "\t<project name>",  #shows when ;help [command] called
        brief="Create a personal project"  #shows when ;help is called 
    )
    async def addmyproj(self, ctx, *args):
        AgendaType = "MyProject"
        if (len(args) < 1):
            await ctx.send(
                f"Invalid number of Arguments.\n"
                "The addmproj command requires Project Name argument.\n"
                "Type ;help addmyproj for more information.")
            return

        # Arguments after command are joined and manually separated using specified delimiter ';'
        string = " ".join(args)
        args = string.split(";")
        i = 0
        while i < len(args):
          print(args)
          if len(args[i])<1:
            args.remove(args[i])
            i = i-1
          i+=1
        if (len(args) > 3):
            await ctx.send(f"Invalid number of Arguments.\n"
                           "More arguments than required detected.\n"
                           "Type ;help addmyproj for more information.")
            return

        message = await add_agenda(ctx, AgendaType, args)

        await ctx.channel.send(message)  #bot reply

    ## Add Personal Meeting Command
    @commands.command(
        help="Create a personal meeting and store it in the database.\n\n"
        "Format:\n"
        "\t;addmymeet <meeting name>;<Date in mm-dd-yy>;<Time in hh:mm> \n\n"
        "Required Arguments:\n"
        "\t<meeting name>",  #shows when ;help [command] called
        brief="Create a personal meeting"  #shows when ;help is called 
    )
    async def addmymeet(self, ctx, *args):
        AgendaType = "MyMeeting"
        if (len(args) < 1):
            await ctx.send(
                f"Invalid number of Arguments.\n"
                "The addmymeet command requires Meeting Name argument.\n"
                "Type ;help addmymeet for more information.")
            return

        # Arguments after command are joined and manually separated using specified delimiter ';'
        string = " ".join(args)
        args = string.split(";")
        i = 0
        while i < len(args):
          print(args)
          if len(args[i])<1:
            args.remove(args[i])
            i = i-1
          i+=1
        if (len(args) > 3):
            await ctx.send(f"Invalid number of Arguments.\n"
                           "More arguments than required detected.\n"
                           "Type ;help addmymeet for more information.")
            return

        message = await add_agenda(ctx, AgendaType, args)

        await ctx.channel.send(message)  #bot reply

    ## Add Personal Reminder Command
    @commands.command(
        help="Create a personal reminder and store it in the database.\n\n"
        "Format:\n"
        "\t;addmyrem <reminder name>;<Date in mm-dd-yy>;<Time in hh:mm> \n\n"
        "Required Arguments:\n"
        "\t<reminder name>",  #shows when ;help [command] called
        brief="Create a personal reminder"  #shows when ;help is called 
    )
    async def addmyrem(self, ctx, *args):
        AgendaType = "MyReminder"
        if (len(args) < 1):
            await ctx.send(
                f"Invalid number of Arguments.\n"
                "The addmyrem command requires Reminder Name argument.\n"
                "Type ;help addmyrem for more information.")
            return

        # Arguments after command are joined and manually separated using specified delimiter ';'
        string = " ".join(args)
        args = string.split(";")
        i = 0
        while i < len(args):
          print(args)
          if len(args[i])<1:
            args.remove(args[i])
            i = i-1
          i+=1
        if (len(args) > 3):
            await ctx.send(f"Invalid number of Arguments.\n"
                           "More arguments than required detected.\n"
                           "Type ;help addmyrem for more information.")
            return

        message = await add_agenda(ctx, AgendaType, args)

        await ctx.channel.send(message)  #bot reply

class RequestGroupCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Commands

    ## Request Group Task Command - Boilerplate for requesting agenda data commands
    @commands.command(
        help=
        "Request specific group task data from the database\n\n"
        "Format:\n"
        "\t;task <task id>\n\n"
        "Required Arguments:\n"
        "\t<task id> - use command ;tasks to know group task IDs",  #shows when ;help [command] called
        brief="Request group task data"  #shows when ;help is called 
    )
    async def task(self, ctx, *args):
        AgendaType = "Task"
        if (len(args) < 1 or len(args) > 1):
            await ctx.send(f"Invalid number of arguments.\n"
                            "The task command requires only Task ID argument.\n"
                            "Type ;help task for more information.")
            return
        try:
            int(args[0])
        except:
            await ctx.channel.send( "Argument must be integer.\n"
                                    "Type ;help task for more information.")  #bot reply
            return
        # Arguments after command are joined and manually separated using specified delimiter ';'
        string = " ".join(args)
        args = string.split(";")
        
        message = find_agenda(ctx, AgendaType, args)

        await ctx.channel.send(message)  #bot reply

    ## Request Group Project Command
    @commands.command(
        help=
        "Request specific group project data from the database\n\n"
        "Format:\n"
        "\t;proj <proj id>\n\n"
        "Required Arguments:\n"
        "\t<project id> - use command ;projs to know project IDs",  #shows when ;help [command] called
        brief="Request group project data"  #shows when ;help is called 
    )
    async def proj(self, ctx, *args):
        AgendaType = "Project"
        if (len(args) < 1 or len(args) > 1):
            await ctx.send(f"Invalid number of arguments.\n"
                            "The proj command requires only Project ID argument.\n"
                            "Type ;help proj for more information.")
            return
        try:
            int(args[0])
        except:
            await ctx.channel.send( "Argument must be integer.\n"
                                    "Type ;help proj for more information.")  #bot reply
            return
        # Arguments after command are joined and manually separated using specified delimiter ';'
        string = " ".join(args)
        args = string.split(";")
        
        message = find_agenda(ctx, AgendaType, args)

        await ctx.channel.send(message)  #bot reply

    ## Request Group Meeting Command
    @commands.command(
        help=
        "Request specific group meeting data from the database\n\n"
        "Format:\n"
        "\t;meet <meeting id>\n\n"
        "Required Arguments:\n"
        "\t<meeting id> - use command ;meets to know meeting IDs",  #shows when ;help [command] called
        brief="Request group meeting data"  #shows when ;help is called 
    )
    async def meet(self, ctx, *args):
        AgendaType = "Meeting"
        if (len(args) < 1 or len(args) > 1):
            await ctx.send(f"Invalid number of arguments.\n"
                            "The meet command requires only Meeting ID argument.\n"
                            "Type ;help meet for more information.")
            return
        try:
            int(args[0])
        except:
            await ctx.channel.send( "Argument must be integer.\n"
                                    "Type ;help meet for more information.")  #bot reply
            return
        # Arguments after command are joined and manually separated using specified delimiter ';'
        string = " ".join(args)
        args = string.split(";")
        
        message = find_agenda(ctx, AgendaType, args)

        await ctx.channel.send(message)  #bot reply

    ## Request Group Reminder Command
    @commands.command(
        help=
        "Request specific group reminder data from the database\n\n"
        "Format:\n"
        "\t;rem <reminder id>\n\n"
        "Required Arguments:\n"
        "\t<reminder id> - use command ;rems to know reminder IDs",  #shows when ;help [command] called
        brief="Request group reminder data"  #shows when ;help is called 
    )
    async def rem(self, ctx, *args):
        AgendaType = "Reminder"
        if (len(args) < 1 or len(args) > 1):
            await ctx.send(f"Invalid number of arguments.\n"
                            "The rem command requires only Reminder ID argument.\n"
                            "Type ;help rem for more information.")
            return
        try:
            int(args[0])
        except:
            await ctx.channel.send( "Argument must be integer.\n"
                                    "Type ;help rem for more information.")  #bot reply
            return
        # Arguments after command are joined and manually separated using specified delimiter ';'
        string = " ".join(args)
        args = string.split(";")
        
        message = find_agenda(ctx, AgendaType, args)

        await ctx.channel.send(message)  #bot reply
    
    ## Request All Group Tasks Command - 
    @commands.command(
        help=
        "Request all Group Tasks with Task ID from the database. First argument is Role/Group name.\n\n"
        "Format:\n"
        "\t;tasks Role_Name\n\n"
        "Required Arguments:\n"
        "\tNone",  #shows when ;help [command] called
        brief="Request all group tasks"  #shows when ;help is called 
    )
    async def tasks(self, ctx, *args):
        AgendaType = "Task"
        string = " ".join(args)
        args = string.split(";")

        i = 0
        while i < len(args):
          if len(args[i])<1:
            args.remove(args[i])
            i = i-1
          i+=1
            
        if (len(args) > 1):
            await ctx.send(f"Invalid number of Arguments.\n"
                            "The tasks command can accept only 1 argument.\n"
                            "Type ;help tasks for more information.")
            return
        
        message = list_agenda(ctx, AgendaType, args)

        await ctx.channel.send(f"{ctx.author.mention} your group tasks are:\n{message}")  #bot reply
    
    ## Request All Group Projects Command - 
    @commands.command(
        help=
        "Request all Group Projects with Project ID from the database. First argument is Role/Group name.\n\n"
        "Format:\n"
        "\t;projs Role_Name\n\n"
        "Required Arguments:\n"
        "\tNone",  #shows when ;help [command] called
        brief="Request all group projects"  #shows when ;help is called 
    )
    async def projs(self, ctx, *args):
        AgendaType = "Project"
        string = " ".join(args)
        args = string.split(";")

        i = 0
        while i < len(args):
          if len(args[i])<1:
            args.remove(args[i])
            i = i-1
          i+=1
            
        if (len(args) > 1):
            await ctx.send(f"Invalid number of Arguments.\n"
                            "The tasks command can accept only 1 argument.\n"
                            "Type ;help tasks for more information.")
            return

        
        message = list_agenda(ctx, AgendaType, args)

        await ctx.channel.send(f"{ctx.author.mention} your group projects are:\n{message}")  #bot reply

    ## Request All Group Meetings Command - 
    @commands.command(
        help=
        "Request all Group Meetings with Meeting ID from the database. First argument is Role/Group name.\n\n"
        "Format:\n"
        "\t;meets Role_Name\n\n"
        "Required Arguments:\n"
        "\tNone",  #shows when ;help [command] called
        brief="Request all group meetings"  #shows when ;help is called 
    )
    async def meets(self, ctx, *args):
        AgendaType = "Meeting"
        string = " ".join(args)
        args = string.split(";")

        i = 0
        while i < len(args):
          if len(args[i])<1:
            args.remove(args[i])
            i = i-1
          i+=1
            
        if (len(args) > 1):
            await ctx.send(f"Invalid number of Arguments.\n"
                            "The tasks command can accept only 1 argument.\n"
                            "Type ;help tasks for more information.")
            return

        
        message = list_agenda(ctx, AgendaType, args)

        await ctx.channel.send(f"{ctx.author.mention} your group meetings are:\n{message}")  #bot reply

    ## Request All Group Reminders Command - 
    @commands.command(
        help=
        "Request all Group Reminders with Reminder ID from the database. First argument is Role/Group name.\n\n"
        "Format:\n"
        "\t;rems Role_Name\n\n"
        "Required Arguments:\n"
        "\tNone",  #shows when ;help [command] called
        brief="Request all group reminders"  #shows when ;help is called 
    )
    async def rems(self, ctx, *args):
        AgendaType = "Reminder"
        string = " ".join(args)
        args = string.split(";")

        i = 0
        while i < len(args):
          if len(args[i])<1:
            args.remove(args[i])
            i = i-1
          i+=1
            
        if (len(args) > 1):
            await ctx.send(f"Invalid number of Arguments.\n"
                            "The tasks command can accept only 1 argument.\n"
                            "Type ;help tasks for more information.")
            return

        
        message = list_agenda(ctx, AgendaType, args)

        await ctx.channel.send(f"{ctx.author.mention} your group reminders are:\n{message}")  #bot reply

# Add the command group classes
class RequestPersonalCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Commands

    ## Request Personal Task Command
    @commands.command(
        help=
        "Request specific personal task data from the database\n\n"
        "Format:\n"
        "\t;mytask <task id>\n\n"
        "Required Arguments:\n"
        "\t<task id> - use command ;mytasks to know personal task IDs",  #shows when ;help [command] called
        brief="Request personal task data"  #shows when ;help is called 
    )
    async def mytask(self, ctx, *args):
        AgendaType = "MyTask"
        if (len(args) < 1 or len(args) > 1):
            await ctx.send(f"Invalid number of arguments.\n"
                            "The mytask command requires only Task ID argument.\n"
                            "Type ;help mytask for more information.")
            return
        try:
            int(args[0])
        except:
            await ctx.channel.send( "Argument must be integer.\n"
                                    "Type ;help mytask for more information.")  #bot reply
            return
        # Arguments after command are joined and manually separated using specified delimiter ';'
        string = " ".join(args)
        args = string.split(";")
        
        message = personal_find_agenda(ctx, AgendaType, args)

        await ctx.channel.send(message)  #bot reply

    ## Request Personal Project Command
    @commands.command(
        help=
        "Request specific personal project data from the database\n\n"
        "Format:\n"
        "\t;myproj <proj id>\n\n"
        "Required Arguments:\n"
        "\t<project id> - use command ;myprojs to know personal project IDs",  #shows when ;help [command] called
        brief="Request personal project data"  #shows when ;help is called 
    )
    async def myproj(self, ctx, *args):
        AgendaType = "MyProject"
        if (len(args) < 1 or len(args) > 1):
            await ctx.send(f"Invalid number of arguments.\n"
                            "The myproj command requires only Project ID argument.\n"
                            "Type ;help myproj for more information.")
            return
        try:
            int(args[0])
        except:
            await ctx.channel.send( "Argument must be integer.\n"
                                    "Type ;help myproj for more information.")  #bot reply
            return
        # Arguments after command are joined and manually separated using specified delimiter ';'
        string = " ".join(args)
        args = string.split(";")
        
        message = personal_find_agenda(ctx, AgendaType, args)

        await ctx.channel.send(message)  #bot reply

    ## Request Personal Meeting Command
    @commands.command(
        help=
        "Request specific personal meeting data from the database\n\n"
        "Format:\n"
        "\t;mymeet <meeting id>\n\n"
        "Required Arguments:\n"
        "\t<meeting id> - use command ;mymeets to know personal meeting IDs",  #shows when ;help [command] called
        brief="Request personal meeting data"  #shows when ;help is called 
    )
    async def mymeet(self, ctx, *args):
        AgendaType = "MyMeeting"
        if (len(args) < 1 or len(args) > 1):
            await ctx.send(f"Invalid number of arguments.\n"
                            "The mymeet command requires only Meeting ID argument.\n"
                            "Type ;help mymeet for more information.")
            return
        try:
            int(args[0])
        except:
            await ctx.channel.send( "Argument must be integer.\n"
                                    "Type ;help mymeet for more information.")  #bot reply
            return
        # Arguments after command are joined and manually separated using specified delimiter ';'
        string = " ".join(args)
        args = string.split(";")
        
        message = personal_find_agenda(ctx, AgendaType, args)

        await ctx.channel.send(message)  #bot reply
      
    ## Request Personal Reminder Command
    @commands.command(
        help=
        "Request specific personal reminder data from the database\n\n"
        "Format:\n"
        "\t;myrem <reminder id>\n\n"
        "Required Arguments:\n"
        "\t<reminder id> - use command ;myrems to know personal reminder IDs",  #shows when ;help [command] called
        brief="Request personal reminder data"  #shows when ;help is called 
    )
    async def myrem(self, ctx, *args):
        AgendaType = "MyReminder"
        if (len(args) < 1 or len(args) > 1):
            await ctx.send(f"Invalid number of arguments.\n"
                            "The myrem command requires only Reminder ID argument.\n"
                            "Type ;help myrem for more information.")
            return
        try:
            int(args[0])
        except:
            await ctx.channel.send( "Argument must be integer.\n"
                                    "Type ;help myrem for more information.")  #bot reply
            return
        # Arguments after command are joined and manually separated using specified delimiter ';'
        string = " ".join(args)
        args = string.split(";")
        
        message = personal_find_agenda(ctx, AgendaType, args)

        await ctx.channel.send(message)  #bot reply
    
    ## Request All Personal Tasks Command - 
    @commands.command(
        help=
        "Request all Personal Tasks with Task ID and the ones assigned or created by you from the database\n\n"
        "Format:\n"
        "\t;mytasks <Role Name>\n\n"
        "Required Arguments:\n"
        "\tNone",  #shows when ;help [command] called
        brief="Request all personal tasks"  #shows when ;help is called 
    )
    async def mytasks(self, ctx, *args):
        AgendaType = "MyTask"
        string = " ".join(args)
        args = string.split(";")

        i = 0
        while i < len(args):
          if len(args[i])<1:
            args.remove(args[i])
            i = i-1
          i+=1
            
        if (len(args) > 1):
            await ctx.send(f"Invalid number of Arguments.\n"
                            "The mytasks command can accept only 1 argument.\n"
                            "Type ;help mytasks for more information.")
            return

        
        message = personal_list_agenda(ctx, AgendaType, args)

        await ctx.channel.send(f"{ctx.author.mention} your personal tasks are:\n{message}")  #bot reply
    
    ## Request All Personal Projects Command - 
    @commands.command(
        help=
        "Request all Personal Projects with Project ID and the ones assigned or created by you from the database\n\n"
        "Format:\n"
        "\t;myprojs\n\n"
        "Required Arguments:\n"
        "\tNone",  #shows when ;help [command] called
        brief="Request all personal projects"  #shows when ;help is called 
    )
    async def myprojs(self, ctx, *args):
        AgendaType = "MyProject"
        string = " ".join(args)
        args = string.split(";")

        i = 0
        while i < len(args):
          if len(args[i])<1:
            args.remove(args[i])
            i = i-1
          i+=1
            
        if (len(args) > 1):
            await ctx.send(f"Invalid number of Arguments.\n"
                            "The myprojs command can accept only 1 argument.\n"
                            "Type ;help myprojs for more information.")
            return

        
        message = personal_list_agenda(ctx, AgendaType, args)

        await ctx.channel.send(f"{ctx.author.mention} your personal projects are:\n{message}")  #bot reply

    ## Request All Personal Meetings Command - 
    @commands.command(
        help=
        "Request all Personal Meetings with Meeting ID and the ones assigned or created by you from the database\n\n"
        "Format:\n"
        "\t;mymeets\n\n"
        "Required Arguments:\n"
        "\tNone",  #shows when ;help [command] called
        brief="Request all personal meetings"  #shows when ;help is called 
    )
    async def mymeets(self, ctx, *args):
        AgendaType = "MyMeeting"
        string = " ".join(args)
        args = string.split(";")

        i = 0
        while i < len(args):
          if len(args[i])<1:
            args.remove(args[i])
            i = i-1
          i+=1
            
        if (len(args) > 1):
            await ctx.send(f"Invalid number of Arguments.\n"
                            "The mymeets command can accept only 1 argument.\n"
                            "Type ;help mymeets for more information.")
            return

        
        message = personal_list_agenda(ctx, AgendaType, args)

        await ctx.channel.send(f"{ctx.author.mention} your personal meetings are:\n{message}")  #bot reply

    ## Request All Personal Reminders Command - 
    @commands.command(
        help=
        "Request all Personal Reminders with Reminder ID and the ones assigned or created by you from the database\n\n"
        "Format:\n"
        "\t;myrems\n\n"
        "Required Arguments:\n"
        "\tNone",  #shows when ;help [command] called
        brief="Request all personal reminders"  #shows when ;help is called 
    )
    async def myrems(self, ctx, *args):
        AgendaType = "MyReminder"
        string = " ".join(args)
        args = string.split(";")

        i = 0
        while i < len(args):
          if len(args[i])<1:
            args.remove(args[i])
            i = i-1
          i+=1
            
        if (len(args) > 1):
            await ctx.send(f"Invalid number of Arguments.\n"
                            "The myrems command can accept only 1 argument.\n"
                            "Type ;help myrems for more information.")
            return

        
        message = personal_list_agenda(ctx, AgendaType, args)

        await ctx.channel.send(f"{ctx.author.mention} your personal reminders are:\n{message}")  #bot reply

class UpdateCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Commands

    ## Delete Task Command -
    @commands.command(
        help=
        "Delete specific agenda from the database\n\n"
        "Format:\n"
        "\t;delete <agenda type> <agenda id>\n\n"
        "Required Arguments:\n"
        "\t<agenda type> - Task, Project, Meeting, Reminder\n\n"
        "\t<agenda id> - use command ;mytasks, ;myprojs, ;mymeets, ;myrems to know the agenda IDs",  #shows when ;help [command] called
        brief="Delete an agenda"  #shows when ;help is called 
    )
    async def delete(self, ctx, *args):
        if (len(args) < 2 or len(args) > 2):
            await ctx.send(f"Invalid number of arguments.\n"
                            "The delete command requires Agenda Type and Agenda ID argument.\n"
                            "Type ;help delete for more information.")
            return
        if args[0] not in ["Task", "Project", "Meeting", "Reminder"]:
            await ctx.send(f"Invalid Agenda Type.\n"
                            "The delete command requires Agenda Type and Agenda ID argument.\n"
                            "Type ;help delete for more information.")
            return
        try:
            int(args[1])
        except:
            await ctx.channel.send( "Second Argument must be integer.\n"
                                    "Type ;help delete for more information.")  #bot reply
            return
        
        
        message = delete_agenda(ctx, args)

        await ctx.channel.send(message)  #bot reply
      
    ## More Update commands

    # ;updatename <AgendaType>;<AgendaID>;<NewName>
        # <AgendaType> - Error if type does not exist
        # <AgendaID> - Error if data does not exist (i.e. wala pang task 3 but u tryna update it already)
    @commands.command(
        help=
        "Delete specific agenda from the database\n\n"
        "Format:\n"
        "\t;delete <agenda type> <agenda id>\n\n"
        "Required Arguments:\n"
        "\t<agenda type> - Task, Project, Meeting, Reminder\n\n"
        "\t<agenda id> - use command ;mytasks, ;myprojs, ;mymeets, ;myrems to know the agenda IDs",  #shows when ;help [command] called
        brief="Delete an agenda"  #shows when ;help is called 
    )
    async def updatename(self, ctx, *args):
        pass
    

    # ;updatedue <AgendaType>;<AgendaID>;<NewDueDate> 
        # <AgendaType> - Error if type does not exist
        # <AgendaID> - Error if data does not exist (i.e. wala pang task 3 but u tryna update it already)
        # <NewDueDate> - Error if: 
                            # - di datetime and 
                            # - if it is earlier than today (?)
    @commands.command(
        help=
        "Delete specific agenda from the database\n\n"
        "Format:\n"
        "\t;delete <agenda type> <agenda id>\n\n"
        "Required Arguments:\n"
        "\t<agenda type> - Task, Project, Meeting, Reminder\n\n"
        "\t<agenda id> - use command ;mytasks, ;myprojs, ;mymeets, ;myrems to know the agenda IDs",  #shows when ;help [command] called
        brief="Delete an agenda"  #shows when ;help is called 
    )
    async def updatedue(self, ctx, *args):
        pass


    # ;assign <AgendaType>;<AgendaID>;<NewUser> (Throw error if not in your group/your server yung user)
        # <AgendaType> - Error if type does not exist
        # <AgendaID> - Error if:
                        # - data does not exist (i.e. wala pang task 3 but u tryna update it already)
                        # - not an agenda of your group
        # <NewUser> - Error if:
                        # - not in your group (compare member.roles to agenda's "GroupID" attribute)
                        # - not a member of the server
    @commands.command(
        help=
        "Delete specific agenda from the database\n\n"
        "Format:\n"
        "\t;delete <agenda type> <agenda id>\n\n"
        "Required Arguments:\n"
        "\t<agenda type> - Task, Project, Meeting, Reminder\n\n"
        "\t<agenda id> - use command ;mytasks, ;myprojs, ;mymeets, ;myrems to know the agenda IDs",  #shows when ;help [command] called
        brief="Delete an agenda"  #shows when ;help is called 
    )
    async def assign(self, ctx, *args):
        pass


    # ;rem <AgendaType>;<AgendaID>;<NewUser> (Throw error if not in your group/your server yung user)
        # <TaskID> - Error if:
                        # - data does not exist (i.e. wala pang task 3 but u tryna update it already)
                        # - not an agenda of your group
        # <NewUser> - Error if:
                        # - not in your group (compare member.roles to agenda's "GroupID" attribute)
                        # - not a member of the server

    @commands.command(
        help=
        "Delete specific agenda from the database\n\n"
        "Format:\n"
        "\t;delete <agenda type> <agenda id>\n\n"
        "Required Arguments:\n"
        "\t<agenda type> - Task, Project, Meeting, Reminder\n\n"
        "\t<agenda id> - use command ;mytasks, ;myprojs, ;mymeets, ;myrems to know the agenda IDs",  #shows when ;help [command] called
        brief="Delete an agenda"  #shows when ;help is called 
    )
    async def remind(self, ctx, *args):
        pass

    @commands.command(
        help=
        "Create a Poll about a specific agenda from the database\n\n"
        "Format:\n"
        "\t;poll <agenda type>;<agenda id>;<poll question>;<options>*\n\n"
        "Required Arguments:\n"
        "\t<agenda type> - Task, Project, Meeting, Reminder\n\n"
        "\t<agenda id> - use command ;tasks, ;projs, ;meets, ;rems to know the agenda IDs\n\n"
        "\t<poll question> - Type here your question for the task\n\n"
        "\t<options> - The options for this poll separated by semicolons",  #shows when ;help [command] called
        brief="Create a poll about an agenda"  #shows when ;help is called 
    )

    # Prototype only, taken from stackoverflow
    async def poll(self, ctx, *args):
        await ctx.send("Hello")
        if (len(args) < 1):
            await ctx.send(f"Invalid number of Arguments.\n"
                           "The poll command requires at least 5 arguments.\n"
                           "Type ;help poll for more information.")
            return

        # Arguments after command are joined and manually separated using specified delimiter ';'
        string = " ".join(args)
        args = string.split(";")

        i = 0
        while i < len(args):
          if len(args[i])<1:
            args.remove(args[i])
            i = i-1
          i+=1


        # Function starts here
        message = await poll_agenda(ctx, args)
        
        

        
    
    # async def addmytask(self, ctx, *args):
    #     AgendaType = "MyTask"
    #     print(len(args))
    #     if (len(args) < 1):
    #         await ctx.send(f"Invalid number of Arguments.\n"
    #                        "The addmtask command requires Task Name argument.\n"
    #                        "Type ;help addmytask for more information.")
    #         return

    #     # Arguments after command are joined and manually separated using specified delimiter ';'
    #     string = " ".join(args)
    #     args = string.split(";")

    #     i = 0
    #     while i < len(args):
    #       print(args)
    #       if len(args[i])<1:
    #         args.remove(args[i])
    #         i = i-1
    #       i+=1
            
    #     if (len(args) > 3):
    #         await ctx.send(f"Invalid number of Arguments.\n"
    #                        "More arguments than required detected.\n"
    #                        "Type ;help addmytask for more information.")
    #         return

    #     message = await add_agenda(ctx, AgendaType, args)

    #     await ctx.channel.send(message)  #bot reply

class RequestSummaryCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Commands

    @commands.command(
        help=
        "Request all Agenda, even those not assigned to you, for all your groups for today from the database\n\n"
        "Format:\n"
        "\t;day\n\n"
        "Required Arguments:\n"
        "\tNone",  #shows when ;help [command] called
        brief="Request all group agenda for today"  #shows when ;help is called 
    )
    async def day(self, ctx, *args):
            
        if (len(args) > 0):
            await ctx.send(f"Invalid number of Arguments.\n"
                            "The day command accepts no argument.\n"
                            "Type ;help day for more information.")
            return

        
        message = summary_agenda(ctx,"Day")

        await ctx.channel.send(f"{ctx.author.mention} your group Agenda for today are:\n{message}")  #bot reply

    @commands.command(
        help=
        "Request all Agenda, even those not assigned to you, for all your groups for this week from the database\n\n"
        "Format:\n"
        "\t;week\n\n"
        "Required Arguments:\n"
        "\tNone",  #shows when ;help [command] called
        brief="Request all group agenda for this week"  #shows when ;help is called 
    )
    async def week(self, ctx, *args):
            
        if (len(args) > 0):
            await ctx.send(f"Invalid number of Arguments.\n"
                            "The week command accepts no argument.\n"
                            "Type ;help week for more information.")
            return

        
        message = summary_agenda(ctx,"Week")

        await ctx.channel.send(f"{ctx.author.mention} your group Agenda for this week are:\n{message}")  #bot reply

    @commands.command(
        help=
        "Request all Agenda, even those not assigned to you, for all your groups for this month from the database\n\n"
        "Format:\n"
        "\t;month\n\n"
        "Required Arguments:\n"
        "\tNone",  #shows when ;help [command] called
        brief="Request all group agenda for this month"  #shows when ;help is called 
    )
    async def month(self, ctx, *args):
            
        if (len(args) > 0):
            await ctx.send(f"Invalid number of Arguments.\n"
                            "The month command accepts no argument.\n"
                            "Type ;help month for more information.")
            return

        
        message = summary_agenda(ctx,"Month")

        await ctx.channel.send(f"{ctx.author.mention} your group Agenda for this month are:\n{message}")  #bot reply

    @commands.command(
        help=
        "Request all Personal Agenda (and those assigned to you in your groups) for today from the database\n\n"
        "Format:\n"
        "\t;myday\n\n"
        "Required Arguments:\n"
        "\tNone",  #shows when ;help [command] called
        brief="Request all personal agenda for today"  #shows when ;help is called 
    )
    async def myday(self, ctx, *args):
            
        if (len(args) > 0):
            await ctx.send(f"Invalid number of Arguments.\n"
                            "The myday command accepts no argument.\n"
                            "Type ;help myday for more information.")
            return

        
        message = personal_summary_agenda(ctx,"Day")

        await ctx.channel.send(f"{ctx.author.mention} your personal Agenda for today are:\n{message}")  #bot reply
    
    @commands.command(
        help=
        "Request all Personal Agenda (and those assigned to you in your groups) for this week from the database\n\n"
        "Format:\n"
        "\t;myweek\n\n"
        "Required Arguments:\n"
        "\tNone",  #shows when ;help [command] called
        brief="Request all personal agenda for this week"  #shows when ;help is called 
    )
    async def myweek(self, ctx, *args):
            
        if (len(args) > 0):
            await ctx.send(f"Invalid number of Arguments.\n"
                            "The myweek command accepts no argument.\n"
                            "Type ;help myweek for more information.")
            return

        
        message = personal_summary_agenda(ctx,"Week")

        await ctx.channel.send(f"{ctx.author.mention} your personal Agenda for this week are:\n{message}")  #bot reply

    @commands.command(
        help=
        "Request all Personal Agenda (and those assigned to you in your groups) for this month from the database\n\n"
        "Format:\n"
        "\t;mymonth\n\n"
        "Required Arguments:\n"
        "\tNone",  #shows when ;help [command] called
        brief="Request all personal agenda for this month"  #shows when ;help is called 
    )
    async def mymonth(self, ctx, *args):
            
        if (len(args) > 0):
            await ctx.send(f"Invalid number of Arguments.\n"
                            "The mymonth command accepts no argument.\n"
                            "Type ;help mymonth for more information.")
            return

        
        message = personal_summary_agenda(ctx,"Month")

        await ctx.channel.send(f"{ctx.author.mention} your personal Agenda for this month are:\n{message}")  #bot reply

def setup(bot):
    bot.add_cog(SystemListeners(bot))
    bot.add_cog(ServerCommands(bot))
    bot.add_cog(TestCommands(bot))
    bot.add_cog(CreateGroupCommands(bot))
    bot.add_cog(CreatePersonalCommands(bot))
    bot.add_cog(RequestGroupCommands(bot))
    bot.add_cog(RequestPersonalCommands(bot))
    bot.add_cog(UpdateCommands(bot))
    bot.add_cog(RequestSummaryCommands(bot))
