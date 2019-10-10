import discord
from discord.ext import commands
import asyncio
import os
import random
import markovify
import requests
from subprocess import Popen
from pathlib import Path

# Startup/Setup
if not os.path.exists("queue"):
    Path("queue").touch()
log_path = Path("./logs")
if not log_path.exists():
    log_path.mkdir()
logs = {}
log_files = os.listdir("logs")
for log in range(0, len(log_files)):
    fp = open("logs/{}".format(log_files[log]), "r")
    log_file = log_files[log][:-4]
    logs[log_file] = fp.readlines()
    fp.close()

# Initialise dumping queue
devnull = open(os.devnull, "wb")
Popen(["nohup", "./dumpqueue.py"], stdout=devnull, stderr=devnull)

bot = commands.Bot(command_prefix=".", owner_id=119094696487288833)

@bot.event
async def on_ready():
    print("I am running on {}\nwith the ID {}".format(bot.user.name, str(bot.user.id)))

@bot.command()
async def dump(rx):
    try:
        if rx.author.permissions_in(rx.message.channel).administrator or rx.author.id == 119094696487288833:
            i = 0
            await rx.send("Queueing images...")
            entries = ""
            async for message in rx.message.channel.history():
                if message.author.bot:
                    continue
                elif message.attachments:
                    url = message.attachments[0]["url"]
                    entries += "{} {} {}\n".format(url, str(message.channel.id), str(message.id))
                    i += 1
                else:
                    pass
            with open("queue", "a") as fp:
                fp.write(entries)
                fp.close()
            await rx.send("Queued {} images.".format(i))
            i = 0
            await rx.send("Downloading text...")
            file = open("logs/{}.txt".format(rx.message.channel.id), "w")
            async for message in rx.message.channel.history():
                m = message.content
                if m == "":
                    pass
                elif message.author.bot:
                    pass
                else:
                    file.write(m + "\n")
                    i += 1
                    if i % 1000 == 0:
                        print("Downloaded {} lines.".format(i))
            file.close()
            await rx.send("Collected {} lines of text.".format(i))
        else:
            await rx.send("Administrator only.")
    except:
        pass

bot.run("[REDACTED]")
#bot.change_presence(status=discord.Status.online, activity=discord.Game("pee"))
