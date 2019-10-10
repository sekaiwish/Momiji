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
            c = await rx.message.channel.history().flatten()
            for message in c:
                if message.author.bot:
                    continue
                elif message.attachments:
                    for a in message.attachments:
                        entries += "{} {} {}\n".format(a.url, str(message.channel.id), str(message.id))
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
            for message in c:
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

@bot.command()
async def rl(rx):
    try:
        limit = int(rx.message.content.split(' ')[1])
        if limit > 15:
            limit = 15
    except:
        limit = 1
    quotes = ""
    try:
        if logs[rx.message.channel.id]:
            for i in range(limit):
                quotes += random.choice(logs[rx.message.channel.id])
            try:
                await rx.send(quotes)
            except:
                await rx.send("Awoo... an error has occurred.")
        elif os.path.exists("logs/{}.txt".format(rx.message.channel.id)):
            fp = open("logs/{}.txt".format(rx.message.channel.id), "r")
            log = fp.readlines()
            fp.close()
            for i in range(limit):
                quotes += random.choice(log)
            try:
                await rx.send(quotes)
            except:
                await rx.send("Awoo... an error has occurred.")
        else:
            await rx.send("Awoo... this channel has not been dumped.")
    except KeyError:
        await rx.send("Awoo... this channel has not been dumped.")

bot.run("[REDACTED]")
#bot.change_presence(status=discord.Status.online, activity=discord.Game("pee"))
