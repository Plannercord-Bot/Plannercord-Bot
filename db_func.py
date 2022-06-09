import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import os
from decouple import config
from datetime import datetime, date, timedelta
import asyncio
import emoji

# Import secret mongodb_server, exit if not configured properly
try:
    mongodb_server = config('mongodb_server')
except:
    try:
        mongodb_server = os.environ['mongodb_server']
    except:
        print("Configure mongodb server variable first")
        quit()

# Initialize Mongo Client object from MongoDB Atlass
cluster = MongoClient(mongodb_server)
db = cluster["test"]

"""

Functions

"""


# Sets the server's timezone in the database
# The timezone is important for sending dates/reminders
def set_timezone(guild, offset):
    # The collection (like a sub-database) will depend on the server/guild id
    collection = db[str(guild.id)]
    # In the collection, we will find one document and update it
    collection.find_one_and_update(
        # Find the document with _id set to the server/guild's id
        {'_id': guild.id},
        # Then we use the field update operator $set to set a key-value pair in the document
        {
            '$set': {
                'timezone': [
                    timedelta(hours=offset).days,
                    timedelta(hours=offset).seconds
                ]
            }
        })


# Initializes the server into the database
def make_server_collection(guild):
    # The collection (like a sub-database) will depend on the server/guild id
    collection = db[str(guild.id)]

    # Check if guild already in database, if not, create new collection
    if str(guild.id) not in db.list_collection_names():
        # Insert specific server/guild datasuch as name, time created, timezone (default is +8)
        collection.insert_many([{
            "_id":
            guild.id,
            "type":
            "Server Data",
            "name":
            guild.name,
            "time_created":
            datetime.utcnow(),
            "timezone": [timedelta(hours=8).days,
                         timedelta(hours=8).seconds],
        }, {
            "Type": "AgendaTable",
            "Task": [],
            "Project": [],
            "Reminder": [],
            "Meeting": [],
            "MyTask": [],
            "MyProject": [],
            "MyMeeting": [],
            "MyReminder": [],
        }])
        return False, 0

    # Send guild data back to the bot
    else:
        # Get from the database data for the specific guild/server using guild.id
        server_data = collection.find_one({"_id": guild.id})
        # Convert time saved to server timezone
        t = server_data['timezone']
        delta = timedelta(days=t[0], seconds=t[1])
        local_time = server_data['time_created'] + delta
        return True, local_time

# Function for Bot to add channel to server
async def add_channel(ctx, collection, channel_name):
    channels = [i.name for i in ctx.guild.channels]
    if channel_name not in channels:
        channel = await ctx.guild.create_text_channel(channel_name)
        await channel.send("Start of {} channel".format(channel_name))

        # Add channel to database collection
        try:
            collection.insert_one({
                "_id": "ReminderChannel",
                "ChannelID": channel
            })
        except:
            collection.update_one({
                "_id": "ReminderChannel"
            }, {
                "$set": {
                    "ChannelID": channel
                }
            })
    else:
        # Check if channel exists in server
        for i in ctx.guild.channels:
            if i.name == channel_name:
                channel = i.id
                # Try to add channel to database collection
                try:
                    collection.insert_one({
                        "_id": "ReminderChannel",
                        "ChannelID": channel
                    })
                except:
                    collection.update_one({
                        "_id": "ReminderChannel"
                    }, {
                        "$set": {
                            "ChannelID": channel
                        }
                    })
                break

# This is executed at the start of the bot and runs every 60 seconds to run periodic tasks (like reminders)
async def periodic_checker(bot): 
    
    while(True):
        print()
        now = datetime.utcnow()
        print("Now: " + str(datetime.utcnow()))
        # Compute for next minute store in "then"
        then = now + timedelta(minutes=1)       # The next time when this function will run (The one we will compare with the reminder date and time)
        then = then.replace(second=0, microsecond=0)
        # Compute for wait time in seconds
        wait_time = (then - now).total_seconds()                                   # The total time to wait until the next run
        print("Wait Time: " + str(wait_time))
        # Sleep for waittime
        await asyncio.sleep(wait_time)                                                           # Wait until the next run

        # FUNCTIONS TO RUN AFTER HERE

        await agendaTimeCheck(bot, then)                                              # Check if any agenda is due for notification

async def delCollection(ctx):
    ctx.guild.id
    db.drop_collection(str(ctx.guild.id))
    pass



# Function that enters agenda data into the database, requires AgendaType, and the arguments entered
async def add_agenda(ctx, AgendaType, args):
    # Only proceed if server is registered
    if str(ctx.guild.id) not in db.list_collection_names():
        return "Server not yet registered in the database. Please register with the command ;server_register"

    # The collection (like a sub-database) will depend on the server/guild id
    collection = db[str(ctx.guild.id)]

    # Add channel named bot-reminders
    await add_channel(ctx, collection, "bot-reminders")

    # Separate args into useful
    args = [i.strip() for i in args]
    args = [i.strip() for i in args if i != '']

    # Parse DateTime from args
    # Check if Date and Time are present or valid

    # Get timezone from database
    server_data = collection.find_one({"_id": ctx.guild.id})
    t = server_data['timezone']
    # Delta is the offset (+8 hours for Manila, Philippines)
    delta = timedelta(days=t[0], seconds=t[1])

    # Set default
    newdate = datetime.utcnow() + delta
    newtime = "00:00"

    # Default DateTime to be sent is today with hour and minute set to 0
    newdatetime = newdate.replace(hour=0, minute=0)

    # Check if there are Date/Time arguments
    if len(args) == 2:
        # Check if first argument is date
        try:
            # If yes, change
            newdate = datetime.strptime(args[1], "%m-%d-%y")
            newdatetime = newdatetime.replace(month=newdate.month,
                                              day=newdate.day,
                                              year=newdate.year,
                                              second=0,
                                              microsecond=0)
        except:
            # If not date, maybe it is time
            try:
                newdate = datetime.utcnow() + delta
                newtime = datetime.strptime(args[1], "%H:%M")
                newdatetime = newdate.replace(hour=newtime.hour,
                                              minute=newtime.minute,
                                              second=0,
                                              microsecond=0)
            except:
                return "Invalid Date or Time format.\nMake sure it follows the right format:\nDate:\tmm-dd-yy\nTime:\thh:mm"

    # Check if the 3 arguments are data and time
    if len(args) == 3:
        try:
            newdatetime = datetime.strptime(args[1] + "," + args[2],
                                            "%m-%d-%y,%H:%M")
        except:
            return "Invalid Date or Time format.\nMake sure it follows the right format:\nDate:\tmm-dd-yy\nTime:\thh:mm"

    # Now we get the local time + timezone offset from UTC
    local_time = datetime.utcnow() + delta
    # Check if date time input is in the past or future
    if len(args) > 1 and newdatetime < local_time:
        return "Date and/or time not valid.\nMake sure it is scheduled for the future."
    elif len(args) > 1 and newdatetime > local_time:
        # If it is valid, then we can replace args[1] to the valid newdatetime and pop the last argument (if more than 2 args)
        args[1] = newdatetime
        if len(args) == 3:
            args.pop()

    authorID = ctx.author.id
    authorName = ctx.author.name
    authorRoles = [i.id for i in ctx.author.roles]
    data = collection.find_one({
        "Type": "Agenda",
        "AgendaType": AgendaType,
        "AuthorID": authorID,
        "Assigned": authorID,
        "Args": args,
        "GroupID" : authorRoles[-1]
    })
    if data == None:
        collection.insert_one({
            "Type": "Agenda",
            "AgendaType": AgendaType,
            "AuthorID": authorID,
            "Assigned": authorID,
            "Args": args,
            "GroupID" : authorRoles[-1]
        })
        currentAgenda = collection.find_one({
            "Type": "Agenda",
            "AgendaType": AgendaType,
            "AuthorID": authorID,
            "Assigned": authorID,
            "Args": args,
            "GroupID" : authorRoles[-1]
        })
        table = collection.find_one({"Type": "AgendaTable"})

        table[AgendaType].append(currentAgenda['_id'])
        collection.update_one({"Type": "AgendaTable"},
                              {'$set': {
                                  AgendaType: table[AgendaType]
                              }})

        message = f"{AgendaType} added successfully!"
    else:
        message = f"Data already exists. \nTo update, use ;update <agenda> command."
    return message


# Function that enters agenda data into the database, requires AgendaType, and the arguments entered
def find_agenda(ctx, AgendaType, args):

    # Only proceed if server is registered
    if str(ctx.guild.id) not in db.list_collection_names():
        return "Server not yet registered in the database. Please register with the command ;server_register"


    # The collection (like a sub-database) will depend on the server/guild id
    collection = db[str(ctx.guild.id)]

    # Separate args into useful
    args = [i.strip() for i in args]
    args = [i.strip() for i in args if i != '']

    authorID = ctx.author.id
    authorName = ctx.author.name
    authorRoles = [i.id for i in ctx.author.roles]

    table = collection.find_one({"Type": "AgendaTable"})
    AgendaIDList = table[AgendaType]

    if (int(args[0]) > len(AgendaIDList) - 1):
        return "Sorry, that {} does not yet exist.".format(AgendaType)




    # Data Querying

    data = collection.find_one({"_id": AgendaIDList[int(args[0])]})

    # Check if user is allowed to view the data (check if user is the author or if user is in the same group)
    if data["GroupID"] not in authorRoles and data["AuthorID"] != authorID and data["Assigned"] != authorID:
        return "You do not have the permission to view this {}.".format(AgendaType)

    members = {}

    # Temporarily store member display names
    for i in ctx.guild.members:
        members[i.id] = i.display_name

    # Check if data of agenda exists

    if data == None:
        return "Sorry, that {} does not yet exist.".format(AgendaType)
    else:

        # Data Formatting

        message = ""
        for i in data:
            # If attribute is AuthorID and Assigned, substitute to Display name
            if (str(i) == "AuthorID" or str(i) == "Assigned"):
                data[i] = members[data[i]]

            # Do not include attributes _id and Type in message
            Exclude = ["Type", "_id", "Args"]
            if (str(i) not in Exclude):
                toSend = data[i]
                if (i == "AuthorID"):
                    i = "Made by"
                elif (i == "Assigned"):
                    i = "Assigned to"
                elif (i == "AgendaType"):
                    i = "Type"
                message += str(i) + ": " + str(toSend) + "\n"
        args = data['Args']
        for i in range(len(args)):
            attributes = ["Name: ", "Date & Time: "]
            message += attributes[i] + str(args[i]) + "\n"

        message = "Here's what I found:\n\n" + message
    return message

def personal_find_agenda(ctx, AgendaType, args):

    # Only proceed if server is registered
    if str(ctx.guild.id) not in db.list_collection_names():
        return "Server not yet registered in the database. Please register with the command ;server_register"


    # The collection (like a sub-database) will depend on the server/guild id
    collection = db[str(ctx.guild.id)]

    # Separate args into useful
    args = [i.strip() for i in args]
    args = [i.strip() for i in args if i != '']

    authorID = ctx.author.id
    authorName = ctx.author.name
    authorRoles = [i.id for i in ctx.author.roles]

    table = collection.find_one({"Type": "AgendaTable"})
    AgendaIDList = table[AgendaType]

    if (int(args[0]) > len(AgendaIDList) - 1):
        return "Sorry, that {} does not yet exist.".format(AgendaType)




    # Data Querying

    data = collection.find_one({"_id": AgendaIDList[int(args[0])]})

    # Check if user is allowed to view the data (check if user is the author or if user is in the same group)
    if data["AuthorID"] != authorID or data["Assigned"] != authorID:
        return "You do not have the permission to view this {}.".format(AgendaType[2:])

    members = {}

    # Temporarily store member display names
    for i in ctx.guild.members:
        members[i.id] = i.display_name

    # Check if data of agenda exists

    if data == None:
        return "Sorry, that {} does not yet exist.".format(AgendaType)
    else:

        # Data Formatting

        message = ""
        for i in data:
            # If attribute is AuthorID and Assigned, substitute to Display name
            if (str(i) == "AuthorID" or str(i) == "Assigned"):
                data[i] = members[data[i]]

            # Do not include attributes _id and Type in message
            Exclude = ["Type", "_id", "Args"]
            if (str(i) not in Exclude):
                toSend = data[i]
                if (i == "AuthorID"):
                    i = "Made by"
                elif (i == "Assigned"):
                    i = "Assigned to"
                elif (i == "AgendaType"):
                    i = "Type"
                message += str(i) + ": " + str(toSend) + "\n"
        args = data['Args']
        for i in range(len(args)):
            attributes = ["Name: ", "Date & Time: "]
            message += attributes[i] + str(args[i]) + "\n"

        message = "Here's what I found:\n\n" + message
    return message

# Function that lists agenda by agendaType as asked by Author and Assigned
def list_agenda(ctx, AgendaType, args=None):
    # Only proceed if server is registered
    if str(ctx.guild.id) not in db.list_collection_names():
        return "Server not yet registered in the database. Please register with the command ;server_register"


    # The collection (like a sub-database) will depend on the server/guild id
    collection = db[str(ctx.guild.id)]
    authorRoles = [i.name for i in ctx.author.roles]
    authorID = ctx.author.id
    authorRoleIDList = []

    # Separate args into useful
    if args != None and len(args) != 0:
        # Checking for specific group tasks
        args = [i.strip() for i in args]
        args = [i.strip() for i in args if i != '']
        if args[0] not in authorRoles:
            return "Group/Role not found."              # If author not member of group/role entered, return

        for i in ctx.author.roles:
            if i.name == args[0]:
                authorRoleIDList.append(i.id)
                break
    else:
        # Check for all tasks in all roles
        authorRoleIDList = [i.id for i in ctx.author.roles]
    
    # Data Querying, get the AgendaTable
    table = collection.find_one({"Type": "AgendaTable"})

    message = ""
    for RoleID in authorRoleIDList:
        submessage = ""
        Role = ctx.guild.get_role(RoleID)
        RoleName = Role.name
        if(RoleName == "@everyone"):
            RoleName = "everyone"
        submessage += "{}:\n".format(RoleName) 
        AgendaIDList = table[AgendaType]
        

        # Check each entry in the AgendaTable
        if (len(AgendaIDList) > 0):
            for i in AgendaIDList:
                agendaDetails = collection.find_one({"_id": i})
                agendaArguments = agendaDetails['Args']
                agendaName = agendaArguments[0]
                
                # List only if user is allowed to view the data (check if user is the author or if user is in the same group)
                if agendaDetails["GroupID"] == RoleID:
                    submessage += AgendaType + " " + str(AgendaIDList.index(i)) + " \t" + agendaName + "\n"
                else:
                    continue

                # Append to message
            if submessage == "{}:\n".format(RoleName):
                submessage += "Nothing found."
        else:
            submessage += "Nothing found."
        message += submessage +"\n"

    return message


def personal_list_agenda(ctx, AgendaType, args):
    # Only proceed if server is registered
    if str(ctx.guild.id) not in db.list_collection_names():
        return "Server not yet registered in the database. Please register with the command ;server_register"

    print("1")
    # The collection (like a sub-database) will depend on the server/guild id
    collection = db[str(ctx.guild.id)]
    authorRoles = [i.name for i in ctx.author.roles]
    authorID = ctx.author.id
    authorRoleIDList = []
    print("2")
    # Separate args into useful
    # Check if there is a specified Group/Role asked
    if args != None and len(args) != 0:
        # Checking for specific group tasks
        args = [i.strip() for i in args]
        args = [i.strip() for i in args if i != '']
        if args[0] not in authorRoles:
            return "Group/Role not found."          # If author not member of group/role entered, return
        for i in ctx.author.roles:
            if i.name == args[0]:
                authorRoleIDList.append(i.id)
                break
    else:
        # If not Store All Roles/Groups of author
        authorRoleIDList = [i.id for i in ctx.author.roles]
    print("3")
    # Data Querying, get the AgendaTable
    table = collection.find_one({"Type": "AgendaTable"})

    # AgendaTypes = [AgendaType]
    # if AgendaType in ["MyTask","MyProject", "MyMeeting", "MyReminder"]:
    #     AgendaTypes.append(AgendaType[2:])
    message = ""
    if args == None or len(args) == 0:
        print("4")
    # Personal Agenda first (Non-group)
        message += "Personal {}s:\n".format(AgendaType[2:])
        AgendaIDList = table[AgendaType]

        # Check each entry in the AgendaTable
        if (len(AgendaIDList) > 0):
            for i in AgendaIDList:
                agendaDetails = collection.find_one({"_id": i})
                agendaArguments = agendaDetails['Args']
                agendaName = agendaArguments[0]
                
                # List only if user is allowed to view the data (check if user is the author or if user is in the same group)
                if agendaDetails["AuthorID"] != authorID and agendaDetails["Assigned"] != authorID:
                    continue

                # Append to message
                message += AgendaType + " " + str(
                    AgendaIDList.index(i)) + " \t" + agendaName + "\n"
            if len(message) == 0:
                message += "Nothing found for you."
        else:
            message += "Nothing found."

    AgendaType = AgendaType[2:]
    # Group Agenda (only assigned to the user)
    message += "\nGroup {}s:\n".format(AgendaType)
    for RoleID in authorRoleIDList:
        submessage = ""
        Role = ctx.guild.get_role(RoleID)
        RoleName = Role.name
        if(RoleName == "@everyone"):
            RoleName = "everyone"
        submessage += "{}:\n".format(RoleName) 
        AgendaIDList = table[AgendaType]
        

        # Check each entry in the AgendaTable
        if (len(AgendaIDList) > 0):
            for i in AgendaIDList:
                agendaDetails = collection.find_one({"_id": i})
                agendaArguments = agendaDetails['Args']
                agendaName = agendaArguments[0]
                
                # List only if user is allowed to view the data (check if user is the author or if user is in the same group)
                if agendaDetails["GroupID"] == RoleID and (agendaDetails["AuthorID"] == authorID or agendaDetails["Assigned"] == authorID):
                    submessage += AgendaType + " " + str(AgendaIDList.index(i)) + " \t" + agendaName + "\n"

                else:
                    continue
                
            if submessage == "{}:\n".format(RoleName):
                submessage += "Nothing found."
        else:
            submessage += "Nothing found."
        message += submessage +"\n"
    message += "\n"

    return message

def change_agenda_name(ctx, AgendaType, args):

    # Only proceed if server is registered
    if str(ctx.guild.id) not in db.list_collection_names():
        return "Server not yet registered in the database. Please register with the command ;server_register"
    
    if AgendaType in ["MyTask", "MyProject", "MyMeeting", "MyReminder"]:
        return "You cannot assign personal agenda to other users."
    
    # Separate args into useful
    args = [i.strip() for i in args]
    args = [i.strip() for i in args if i != '']

    task_name = args[1]



    # The collection (like a sub-database) will depend on the server/guild id
    collection = db[str(ctx.guild.id)]
    authorID = ctx.author.id


    # Get data from database based on agendatype
    table = collection.find_one({"Type": "AgendaTable"})
    AgendaIDList = table[AgendaType]

        

    try:
        AgendaID = int(args[0])
    except ValueError:
        return "Please specify the ID of the agenda you want to change."

    if AgendaID >= len(AgendaIDList):
        return "Agenda ID not found."
    if AgendaID < 0:
        return "Agenda ID not found."

    # Check if the user is allowed to change the agenda
    agendaData = collection.find_one({"_id": AgendaIDList[AgendaID]})

    if agendaData["AuthorID"] != authorID and agendaData["Assigned"] != authorID:
        return "You are not allowed to change this agenda's details."

    # Change the args
    new_args = agendaData["Args"]

    # Change the task name to task_name
    new_args[0] = task_name
    collection.update_one({"_id": AgendaIDList[AgendaID]}, {"$set": {"Args": new_args}})
    return "Agenda details changed."


def change_agenda_due(ctx, AgendaType, args):

    # Only proceed if server is registered
    if str(ctx.guild.id) not in db.list_collection_names():
        return "Server not yet registered in the database. Please register with the command ;server_register"
    
    if AgendaType in ["MyTask", "MyProject", "MyMeeting", "MyReminder"]:
        return "You cannot assign personal agenda to other users."


    # Separate args into useful
    args = [i.strip() for i in args]
    args = [i.strip() for i in args if i != '']

    # The collection (like a sub-database) will depend on the server/guild id
    collection = db[str(ctx.guild.id)]

    # Check if Date and Time are present or valid

    # Get timezone from database
    server_data = collection.find_one({"_id": ctx.guild.id})
    t = server_data['timezone']
    # Delta is the offset (+8 hours for Manila, Philippines)
    delta = timedelta(days=t[0], seconds=t[1])

    # Set default
    newdate = datetime.utcnow() + delta
    newtime = "00:00"

    # Default DateTime to be sent is today with hour and minute set to 0
    newdatetime = newdate.replace(hour=0, minute=0)

    # Check if there are Date/Time arguments
    if len(args) == 2:
        # Check if first argument is date
        try:
            # If yes, change
            newdate = datetime.strptime(args[1], "%m-%d-%y")
            newdatetime = newdatetime.replace(month=newdate.month,
                                              day=newdate.day,
                                              year=newdate.year,
                                              second=0,
                                              microsecond=0)
        except:
            # If not date, maybe it is time
            try:
                newdate = datetime.utcnow() + delta
                newtime = datetime.strptime(args[1], "%H:%M")
                newdatetime = newdate.replace(hour=newtime.hour,
                                              minute=newtime.minute,
                                              second=0,
                                              microsecond=0)
            except:
                return "Invalid Date or Time format.\nMake sure it follows the right format:\nDate:\tmm-dd-yy\nTime:\thh:mm"

    # Check if the arguments are data and time
    if len(args) == 3:
        try:
            newdatetime = datetime.strptime(args[1] + "," + args[2],
                                            "%m-%d-%y,%H:%M")
        except:
            return "Invalid Date or Time format.\nMake sure it follows the right format:\nDate:\tmm-dd-yy\nTime:\thh:mm"

    # Now we get the local time + timezone offset from UTC
    local_time = datetime.utcnow() + delta
    # Check if date time input is in the past or future
    if len(args) > 1 and newdatetime < local_time:
        return "Date and/or time not valid.\nMake sure it is scheduled for the future."
    elif len(args) > 1 and newdatetime > local_time:
        # If it is valid, then we can replace args[1] to the valid newdatetime and pop the last argument (if more than 2 args)
        args[1] = newdatetime
        if len(args) == 3:
            args.pop()

    
    authorID = ctx.author.id


    # Get data from database based on agendatype
    table = collection.find_one({"Type": "AgendaTable"})
    AgendaIDList = table[AgendaType]



    try:
        AgendaID = int(args[0])
    except ValueError:
        return "Please specify the ID of the agenda you want to change."

    if AgendaID >= len(AgendaIDList):
        return "Agenda ID not found."
    if AgendaID < 0:
        return "Agenda ID not found."

    # Check if the user is allowed to change the agenda
    agendaData = collection.find_one({"_id": AgendaIDList[AgendaID]})

    if agendaData["AuthorID"] != authorID and agendaData["Assigned"] != authorID:
        return "You are not allowed to change this agenda's details."

    # Change the args
    new_args = agendaData["Args"]

    # Change the task name to task_name
    new_args[1] = args[1]
    collection.update_one({"_id": AgendaIDList[AgendaID]}, {"$set": {"Args": new_args}})
    return "Agenda details changed."


def change_assigned(ctx, AgendaType, args):
    # Only proceed if server is registered
    if str(ctx.guild.id) not in db.list_collection_names():
        return "Server not yet registered in the database. Please register with the command ;server_register"
    
    if AgendaType in ["MyTask", "MyProject", "MyMeeting", "MyReminder"]:
        return "You cannot assign personal agenda to other users."
    

    # Separate args into useful
    args = [i.strip() for i in args]
    args = [i.strip() for i in args if i != '']


    memberIDs = [str(i.id) for i in ctx.guild.members]
    members = [str(i.name) for i in ctx.guild.members]
    user = args[1]

    print(user[2:-1])
    # Convert the user argument to a member ID
    if (user[2:-1] in memberIDs):
        user = ctx.guild.members[memberIDs.index(user[2:-1])]

    elif (user in members):
        user = ctx.guild.members[members.index(user)]
    else:
        return f"{user} is not a member of the server. Try checking your spelling or capitalization."


    # The collection (like a sub-database) will depend on the server/guild id
    collection = db[str(ctx.guild.id)]
    authorRoles = [i.name for i in user.roles]
    authorID = ctx.author.id
    authorRoleIDList = [i.id for i in user.roles]


    # Get data from database based on agendatype
    table = collection.find_one({"Type": "AgendaTable"})
    AgendaIDList = table[AgendaType]

        

    try:
        AgendaID = int(args[0])
    except ValueError:
        return "Please specify the ID of the agenda you want to change."

    if AgendaID >= len(AgendaIDList):
        return "Agenda ID not found."
    if AgendaID < 0:
        return "Agenda ID not found."
    # Check if the user is allowed to change the agenda
    agendaData = collection.find_one({"_id": AgendaIDList[AgendaID]})

    if agendaData["AuthorID"] != authorID and agendaData["Assigned"] != authorID:
        return "You are not allowed to change this agenda."
    if agendaData["Assigned"] == user.id:
        return "This agenda is already assigned to that user."
    if agendaData["GroupID"] not in authorRoleIDList:
        return f"The user is not a member of the {AgendaType}'s group"
    

    # Change the assigned user
    collection.update_one({"_id": AgendaIDList[AgendaID]}, {"$set": {"Assigned": user.id}})
    return "Assigned user changed."



# Function that updates agenda depending on author permissions (if author is part of group)
def update_agenda(ctx, AgendaType, args):
    # Only proceed if server is registered
    if str(ctx.guild.id) not in db.list_collection_names():
        return "Server not yet registered in the database. Please register with the command ;server_register"



# Checks all Agenda in all collections if there is a Reminder or Deadline (and reminder set for that agenda)
async def agendaTimeCheck(bot, then):
    
    db_collections = db.list_collection_names()                                             # Get the list of collections in the database

    # Iterate through each collection to check if any agenda is due
    for i in db_collections:                        
            try:    # Try first if the collection has an agenda table with contents
                guild = bot.get_guild(int(i))                                               # Get the guild object from discord
                collection = db[i]                                                          # Get the collection object from the database

                t = collection.find_one({"_id": int(i)})['timezone']                        # Find the timezone of the server
                delta = timedelta(days=t[0], seconds=t[1])
                then_with_offset = then + delta

                

                # Get the channel object from the bot
                channel = bot.get_channel(collection.find_one({"_id": "ReminderChannel"})["ChannelID"]) 
                Agenda = collection.find_one({"Type": "AgendaTable"})                       # Get the agenda table from the database


                # Create an agenda list for each discord server
                AgendaList = []
                for i in Agenda:                          # For each agenda type, merge items to master list
                    if i not in ["Type","_id"]:
                        AgendaList.extend(Agenda[i])
                
                
                if (len(AgendaList) > 0):
                # For each agenda in the masterlist, check their details (deadline, reminder) to check if it is due for notification
                    for i in AgendaList:                
                        agenda_details = collection.find_one({"_id": i})      
                        agenda_args = agenda_details["Args"]
                        try:        # Try to check if the agenda has a reminder
                            argPosition = 1
                            if agenda_details["AgendaType"] in ["Reminder", "MyReminder"]:      # This is specific for reminders
                            
                                argPosition = 1
                            else:
                                argPosition = 1

                            alert_time = agenda_args[argPosition]
                            
                            # Compare alert_time to the next minute, if equal, send a message
                            if(alert_time == then_with_offset):
                                message = formattedAlert(agenda_details, guild)
                                message = "{} Alert!\n\n{}\n".format(agenda_details["AgendaType"], message) 
                                await channel.send(message)
                                # collection.delete_one({"_id": i})
                            print("\tAlert Time: " + str(alert_time))
                        except:
                            print("\tNo Rem Time for " + str(i))
                
            except:
                print("No reminder found in collection " + i)   

# Alert message is formatted here:
def formattedAlert(data, guild):
    members = {}
    # Temporarily store member display names
    for i in guild.members:
        members[i.id] = i.mention

    author = ""
    assigned = ""
    message = ""
    for i in data:
        # If attribute is AuthorID and Assigned, substitute to Display name
        if (str(i) == "AuthorID"):
            author = members[data[i]]
            data[i] = author
        if (str(i) == "Assigned"):
            assigned = members[data[i]]
            data[i] = assigned

        # Do not include attributes _id and Type in message
        if (str(i) not in ["Type", "_id", "Args"]):
            toSend = data[i]
            if (i == "AuthorID"):
                i = "Made by"
            elif (i == "Assigned"):
                i = "Assigned to"
            elif (i == "AgendaType"):
                i = "Type"
            message += str(i) + ": " + str(toSend) + "\n"
    args = data['Args']
    for i in range(len(args)):
        attributes = ["Name: ", "Date & Time: "]
        message += attributes[i] + str(args[i]) + "\n"

    return message           




def delete_agenda(ctx, args):
    # args[0] = Agenda Type and args[1] = Agenda ID
    
    # Strip extra spaces from arguments
    args = [i.strip() for i in args]
    args = [i.strip() for i in args if i != '']

    # Only proceed if server is registered
    if str(ctx.guild.id) not in db.list_collection_names():
        return "Server not yet registered in the database. Please register with the command ;server_register"


    # The collection (like a sub-database) will depend on the server/guild id
    collection = db[str(ctx.guild.id)]
    authorRoleIDList = [i.id for i in ctx.author.roles]
    table = collection.find_one({"Type": "AgendaTable"})
    AgendaIDList = table[args[0]]

    # Seek agenda in collection and check permissions
    if(len(AgendaIDList) > 0):
        try:
            AgendaID = AgendaIDList[int(args[1])]
            agendaDetails = collection.find_one({"_id": AgendaID})
            if agendaDetails["GroupID"] in authorRoleIDList and(agendaDetails["AuthorID"] == ctx.author.id and agendaDetails["Assigned"] == ctx.author.id):
                collection.delete_one({"_id": AgendaID})
                collection.update_one({"Type": "AgendaTable"}, {"$pull": {args[0]: AgendaID}})
                return "Agenda deleted."
            else:
                return "You do not have permissions to delete this agenda."
            
        except:
            return f"{args[0]} not found."
        
    else:
        return f"{args[0]} not found."


async def testfunction(ctx):
    pass

async def setDate(ctx, AgendaType, args):
    # Only proceed if server is registered
    if str(ctx.guild.id) not in db.list_collection_names():
        return "Server not yet registered in the database. Please register with the command ;server_register"

    # The collection (like a sub-database) will depend on the server/guild id
    collection = db[str(ctx.guild.id)]
    authorRoleIDList = [i.id for i in ctx.author.roles]
    table = collection.find_one({"Type": "AgendaTable"})
    AgendaIDList = table[AgendaType]

    # Seek agenda in collection and check permissions
    if(len(AgendaIDList) > 0):
        try:
            AgendaID = AgendaIDList[int(args[0])]
            agendaDetails = collection.find_one({"_id": AgendaID})
            if agendaDetails["GroupID"] in authorRoleIDList and(agendaDetails["AuthorID"] == ctx.author.id and agendaDetails["Assigned"] == ctx.author.id):
                collection.update_one({"_id": AgendaID}, {"$set": {"Date": args[1]}})
                return "Date set."
            else:
                return "You do not have permissions to set this date."
            
        except:
            return "Task not found."
        
    else:
        return "Task not found."

# Function for listing all agenda for the day
def summary_agenda(ctx, period):
    # Only proceed if server is registered
    if str(ctx.guild.id) not in db.list_collection_names():
        return "Server not yet registered in the database. Please register with the command ;server_register"

    # The collection (like a sub-database) will depend on the server/guild id
    collection = db[str(ctx.guild.id)]
    authorRoles = [i.name for i in ctx.author.roles]
    authorID = ctx.author.id
    authorRoleIDList = [i.id for i in ctx.author.roles]
    
    # Data Querying, get the AgendaTable
    table = collection.find_one({"Type": "AgendaTable"})

    # Initialize message
    message = ""

    # Iterate through the author's roles
    for RoleID in authorRoleIDList:
        print(RoleID)
        Role = ctx.guild.get_role(RoleID)
        RoleName = Role.name
        if(RoleName == "@everyone"):
            RoleName = "everyone"
        headermessage = "{}:\n".format(RoleName)
        
        message += headermessage
        for AgendaType in ["Task", "Project", "Meeting", "Reminder"]:
            # Initialize submessage per Role/Group
            submessage = ""
            subheadermessage = "\t{}:\n".format(AgendaType)
            AgendaIDList = table[AgendaType]
            

            # Check each entry in the AgendaTable
            if (len(AgendaIDList) > 0):
                for i in AgendaIDList:
                    agendaDetails = collection.find_one({"_id": i})
                    agendaArguments = agendaDetails['Args']
                    agendaName = agendaArguments[0]
                    
                    
                    # List only if user is allowed to view the data (check if user is the author or if user is in the same group)
                    if agendaDetails["GroupID"] != RoleID:
                        continue
                    try:
                        agendaDateTime = agendaArguments[1]
                        agendaTime = agendaDateTime.time()
                        if(period =="Day"):
                        # Check if the date of the agenda is today
                            if agendaDateTime.date() != date.today():
                                continue
                        elif(period =="Month"):
                            if agendaDateTime.date().month != date.today().month:
                                continue
                        elif(period =="Week"):
                            if agendaDateTime.strftime("%U") != date.today().strftime("%U"):
                                continue
                    except:
                        print("No date found")
                        continue

                    
                    # Append to message
                    agendaIndex = AgendaIDList.index(i)
                    submessage += f"\t\t{AgendaType}\t{agendaIndex}\t{agendaName}\t{agendaDateTime.date()}\t{agendaTime}\n"
                if submessage == "":
                    submessage += "\t\tNothing found.\n"
            else:
                submessage += "\t\tNothing found.\n"
            message += subheadermessage + submessage +"\n"

    return message

def personal_summary_agenda(ctx, period):
    # Only proceed if server is registered
    if str(ctx.guild.id) not in db.list_collection_names():
        return "Server not yet registered in the database. Please register with the command ;server_register"

    # The collection (like a sub-database) will depend on the server/guild id
    collection = db[str(ctx.guild.id)]
    authorRoles = [i.name for i in ctx.author.roles]
    authorID = ctx.author.id
    authorRoleIDList = [i.id for i in ctx.author.roles]
    
    # Data Querying, get the AgendaTable
    table = collection.find_one({"Type": "AgendaTable"})

    # Initialize message
    message = ""

    # Personal Agenda First
    message += "Personal:\n"
    for AgendaType in ["MyTask", "MyProject", "MyMeeting", "MyReminder"]:
            # Initialize submessage per Role/Group
            submessage1 = ""
            subheadermessage1 = "\t{}:\n".format(AgendaType)
            AgendaIDList = table[AgendaType]

            # Check each entry in the AgendaTable
            if (len(AgendaIDList) > 0):
                for i in AgendaIDList:
                    agendaDetails = collection.find_one({"_id": i})
                    agendaArguments = agendaDetails['Args']
                    agendaName = agendaArguments[0]
                    
                    
                    # List only if user is allowed to view the data (check if user is the author or if user is in the same group)
                    if agendaDetails["AuthorID"] != authorID and agendaDetails["Assigned"] != authorID:
                        continue
                    try:
                        agendaDateTime = agendaArguments[1]
                        agendaTime = agendaDateTime.time()
                        if(period =="Day"):
                        # Check if the date of the agenda is today
                            if agendaDateTime.date() != date.today():
                                continue
                        elif(period =="Month"):
                            if agendaDateTime.date().month != date.today().month:
                                continue
                        elif(period =="Week"):
                            if agendaDateTime.strftime("%U") != date.today().strftime("%U"):
                                continue
                    except:
                        print("No date found")
                        continue

                    
                    # Append to message
                    agendaIndex = AgendaIDList.index(i)
                    submessage1 += f"\t\t\t{AgendaType}\t{agendaIndex}\t{agendaName}\t{agendaDateTime.date()}\t{agendaTime}\n"
                if submessage1 == "":
                    submessage1 += "\t\t\tNothing found.\n"
            else:
                submessage1 += "\t\t\tNothing found.\n"
            message += subheadermessage1 + submessage1 +"\n"
    message += "Group (only those assigned to you):\n"
    # Iterate through the author's roles
    for RoleID in authorRoleIDList:
        print(RoleID)
        Role = ctx.guild.get_role(RoleID)
        RoleName = Role.name
        if(RoleName == "@everyone"):
            RoleName = "everyone"
        headermessage = "\t{}:\n".format(RoleName)
        
        message += headermessage
        for AgendaType in ["Task", "Project", "Meeting", "Reminder"]:
            # Initialize submessage per Role/Group
            submessage = ""
            subheadermessage = "\t\t{}:\n".format(AgendaType)
            AgendaIDList = table[AgendaType]

            # Check each entry in the AgendaTable
            if (len(AgendaIDList) > 0):
                for i in AgendaIDList:
                    agendaDetails = collection.find_one({"_id": i})
                    agendaArguments = agendaDetails['Args']
                    agendaName = agendaArguments[0]
                    
                    
                    # List only if user is allowed to view the data (check if user is the author or if user is in the same group)
                    if agendaDetails["GroupID"] != RoleID:
                        continue
                    try:
                        agendaDateTime = agendaArguments[1]
                        agendaTime = agendaDateTime.time()
                        if(period =="Day"):
                        # Check if the date of the agenda is today
                            if agendaDateTime.date() != date.today():
                                continue
                        elif(period =="Month"):
                            if agendaDateTime.date().month != date.today().month:
                                continue
                        elif(period =="Week"):
                            if agendaDateTime.strftime("%U") != date.today().strftime("%U"):
                                continue
                    except:
                        print("No date found")
                        continue

                    
                    # Append to message
                    agendaIndex = AgendaIDList.index(i)
                    submessage += f"\t\t\t{AgendaType}\t{agendaIndex}\t{agendaName}\t{agendaDateTime.date()}\t{agendaTime}\n"
                if submessage == "":
                    submessage += "\t\t\tNothing found.\n"
            else:
                submessage += "\t\t\tNothing found.\n"
            message += subheadermessage + submessage +"\n"

    return message

async def poll_agenda(ctx, args):
    
    AgendaType = args[0]
    AgendaID = args[1]
    poll_title = args[2]
    agenda = find_agenda(ctx, AgendaType, [AgendaID])
    if agenda == f"Sorry, that {AgendaType} does not yet exist.":
        await ctx.send(agenda)
        return
    elif agenda == f"You do not have the permission to view or access this {AgendaType}.":
        await ctx.send(agenda)
        return
    args.remove(args[0])
    args.remove(args[0])
    args.remove(args[0])
    description = []
    reactions = [chr(i) for i in range(ord(u"\U0001F1E6"), ord(u"\U0001F1FF") + 1)]
    for x, option in enumerate(args):
        description += '\n {} {}'.format(reactions[x], option)

    poll_embed = discord.Embed(
                                title = poll_title, 
                                color = 0x31FF00, 
                                description = ''.join(description))
    poll_embed.add_field(
                        name = AgendaType, 
                        value = agenda, 
                        inline = False)
    
    poll_embed.add_field(
                        name = "Vote!", 
                        value = "React with the corresponding emoji to vote for your choice.", 
                        inline = False)
    react_message = await ctx.send(embed=poll_embed)

    for i in range(len(args)):
        await react_message.add_reaction(reactions[i])


def add_reminder(ctx, args):
    # Only proceed if server is registered
    if str(ctx.guild.id) not in db.list_collection_names():
        return "Server not yet registered in the database. Please register with the command ;server_register"