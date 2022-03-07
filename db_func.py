import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import os
from decouple import config

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
    if str(guild.id) not in db.list_collection_names():
        collection = db[str(guild.id)]
        collection.insert_many([{"_id":guild.id,"type":"Server Data","name":guild.name}])
    else:
        return True
    
