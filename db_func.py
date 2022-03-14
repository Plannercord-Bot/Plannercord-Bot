import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import os
from decouple import config
from datetime import datetime, timezone, timedelta

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
# Default collection for debugging
collection = db["test_collection"]



"""

Functions

"""


# Sets the server's timezone in the database
# The timezone is important for sending dates/reminders
def set_timezone(guild,offset):
    # The collection (like a sub-database) will depend on the server/guild id
    collection = db[str(guild.id)]
    # In the collection, we will find one document and update it 
    collection.find_one_and_update(
        # Find the document with _id set to the server/guild's id
        {'_id':guild.id},
        # Then we use the field update operator $set to set a key-value pair in the document
        {'$set':
            {
                'timezone':[timedelta(hours=offset).days, timedelta(hours=offset).seconds]
            }
        })


# Initializes the server into the database
def make_server_collection(guild):
  # The collection (like a sub-database) will depend on the server/guild id
    collection = db[str(guild.id)]

    # Check if guild already in database, if not, create new collection
    if str(guild.id) not in db.list_collection_names():
        # Insert specific server/guild datasuch as name, time created, timezone (default is +8)
        collection.insert_many([
            {"_id":guild.id,
            "type":"Server Data",
            "name":guild.name,
            "time_created":datetime.utcnow(),
            "timezone":[timedelta(hours=8).days, timedelta(hours=8).seconds],
            }])
        return False, 0

    # Send guild data back to the bot
    else:
        # Get from the database data for the specific guild/server using guild.id
        server_data = collection.find_one({"_id":guild.id})
        # Convert time saved to server timezone
        t = server_data['timezone']
        delta = timedelta(days = t[0], seconds=t[1])
        local_time = server_data['time_created'] + delta
        return True, local_time


# Function that enters agenda data into the database, requires AgendaType, and the arguments entered
def add_agenda(ctx, AgendaType, args):
  # Only proceed if server is registered
    if str(ctx.guild.id) not in db.list_collection_names():
        return "Server not yet registered in the database. Please register with the command ;server_register"
  # The collection (like a sub-database) will depend on the server/guild id
    collection = db[str(ctx.guild.id)]

    # Separate args into useful
    args = [i.strip() for i in args]
    args = [i.strip() for i in args if i!='']

    authorID = ctx.author.id
    authorName = ctx.author.name
    authorRoles = [i.id for i in ctx.author.roles]

    data = collection.find_one({"Type":"Agenda",
                                "AgendaType":AgendaType, 
                                "AuthorID":authorID, 
                                "Assigned":authorID,
                                "Args":args})
    print(data)
    if data == None:
        collection.insert_one({ "Type":"Agenda",
                                "AgendaType":AgendaType,
                                "AuthorID":authorID, 
                                "Assigned":authorID,
                                "Args":args})
        message = f"{AgendaType} added successfullly!"
    else:
        message = f"Data already exists. \nTo update, use ;update <{AgendaType} name>"
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
    args = [i.strip() for i in args if i!='']

    authorID = ctx.author.id
    authorName = ctx.author.name
    authorRoles = [i.id for i in ctx.author.roles]

    data = collection.find_one({"Type":"Agenda",
                                "AgendaType":AgendaType, 
                                "AuthorID":authorID, 
                                "Assigned":authorID,
                                "Args":args})
    members = {}
    for i in ctx.guild.members:
        members[i.id] = i.display_name
    if data == None:
        message = f"Sorry, that {AgendaType} does not yet exist."
    else:
        message = ""
        for i in data:
            if(str(i) == "AuthorID" or str(i) == "Assigned"):
                data[i] = members[data[i]]
            message += str(i) + ": " +str(data[i]) + "\n"
        message = "Here's what I found:\n" + message 
    return message