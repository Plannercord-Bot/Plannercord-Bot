import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import os
from decouple import config
from datetime import datetime, timezone, timedelta

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


def set_timezone(guild,offset):
    collection = db[str(guild.id)]
    print(type(offset))
    print(collection.find_one({'_id':guild.id}))
    collection.find_one_and_update(
        {'_id':guild.id},
        {'$set':
            {
                'timezone':[timedelta(hours=offset).days, timedelta(hours=offset).seconds]
            }
        })
    print("Done")
    print(collection.find_one({'_id':guild.id}))

def make_server_collection(guild):
    collection = db[str(guild.id)]

    # Check if guild already in database, if not, create new collection with 
    if str(guild.id) not in db.list_collection_names():
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
        server_data = collection.find_one({"_id":guild.id})
        # Covnert time to server timezone
        t = server_data['timezone']
        delta = timedelta(days = t[0], seconds=t[1])
        local_time = server_data['time_created'] + delta
        return True, local_time
    
def add_agenda(guild):
    collection = db[str(guild.id)]
    return