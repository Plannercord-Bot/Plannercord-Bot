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



def make_server_collection(guild):
    collection = db[str(guild.id)]
    if str(guild.id) not in db.list_collection_names():
        collection.insert_many([{"_id":guild.id,"type":"Server Data","name":guild.name,"time":datetime.now(),"timezone":str(timedelta(hours=8))}])
        return False, 0 ,0
    else:
        server_data = collection.find_one({"_id":guild.id})
        t = datetime.strptime(server_data['timezone'],"%H:%M:%S")
        delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        local_time = server_data['time']+delta
        print(server_data['time'])
        print(local_time)
        print(delta)
        return True,local_time,server_data
    
