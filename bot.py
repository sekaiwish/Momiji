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
    fp = open(f"logs/{log_files[log]}", "r")
    log_file = log_files[log][:-4]
    logs[log_file] = fp.readlines()
    fp.close()

# Initialise dumping queue
devnull = open(os.devnull, "wb")
Popen(["nohup", "./dumpqueue.py"], stdout=devnull, stderr=devnull)

bot = commands.Bot(command_prefix=".", owner_id=119094696487288833)

@bot.event
async def on_ready():
    print(f"I am running on {bot.user.name}\nwith the ID {bot.user.id}")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("pee"))

@bot.command()
async def dump(rx):
    try:
        if rx.author.permissions_in(rx.message.channel).administrator or rx.author.id == 119094696487288833:
            i = 0
            await rx.send("Queueing images...")
            entries = ""
            c = await rx.message.channel.history(limit=None).flatten()
            for message in c:
                if message.author.bot:
                    continue
                elif message.attachments:
                    for a in message.attachments:
                        entries += f"{a.url} {message.channel.id} {message.id}\n"
                        i += 1
                else:
                    pass
            with open("queue", "a") as fp:
                fp.write(entries)
                fp.close()
            await rx.send("Queued {} images.".format(i))
            i = 0
            await rx.send("Downloading text...")
            file = open(f"logs/{rx.message.channel.id}.txt", "w")
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
            log = str(rx.message.channel.id) + ".txt"
            fp = open(f"logs/{log}", "r")
            logs[str(rx.message.channel.id)] = fp.readlines()
            fp.close()
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
        if logs[str(rx.message.channel.id)]:
            for i in range(limit):
                quotes += random.choice(logs[str(rx.message.channel.id)])
            try:
                await rx.send(quotes)
            except:
                await rx.send("Awoo... an error has occurred.")
        elif os.path.exists(f"logs/{rx.message.channel.id}.txt"):
            fp = open(f"logs/{rx.message.channel.id}.txt", "r")
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

def rl_inBot(rx):
    try:
        if logs[str(rx.message.channel.id)]:
            return random.choice(logs[str(rx.message.channel.id)])
        elif os.path.exists(f"logs/{rx.message.channel.id}.txt"):
            fp = open(f"logs/{rx.message.channel.id}.txt", "r")
            log = fp.readlines()
            fp.close()
            return random.choice(log)
        else:
            return "Awoo... this channel has not been dumped."
    except KeyError:
        return "Awoo... this channel has not been dumped."

@bot.command()
async def rt(rx):
    try:
        if logs[str(rx.message.channel.id)]:
            text = "".join(logs[str(rx.message.channel.id)])
        elif os.path.exists(f"logs/{rx.message.channel.id}.txt"):
            fp = open(f"logs/{rx.message.channel.id}.txt", "r")
            text = fp.read()
            fp.close()
        else:
            await rx.send("Awoo... this channel has not been dumped.")
        try:
            samples = int(rx.message.content.split(' ')[1])
            if samples > 2000:
                samples = 2000
        except:
            samples = 200
        await rx.send(markovify.Text(text).make_short_sentence(samples))
    except KeyError:
        await rx.send("Awoo... this channel has not been dumped.")

@bot.command()
async def ri(rx):
    directory = str(rx.message.channel.id)
    image = random.choice(os.listdir(directory))
    file = f"{directory}/{image}"
    try:
        await rx.send(file=discord.File(file), content=rl_inBot(rx))
    except:
        print(f"File '{file}' not found.")

@bot.command()
async def rp(rx):
    names = []
    for member in rx.guild.members:
        names.append(member.name)
    text1 = rl_inBot(rx)
    text2 = rl_inBot(rx)
    name1 = random.choice(names)
    name2 = random.choice(names)
    if name1 == name2:
        final = f"{name1}: {text1}\nalso {name2}: {text2}"
    else:
        final = f"{name1}: {text1}\n{name2}: {text2}"
    await rx.send(final)

bot.run("[REDACTED]")
