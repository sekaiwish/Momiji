#!/usr/bin/env python3.5
import discord
from discord.ext import commands
from discord.ext.commands import Bot
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

bot = commands.Bot(command_prefix=".")

@bot.event
async def on_ready():
    print("I am running on {}\nwith the ID {}".format(bot.user.name, bot.user.id))

@bot.event
async def on_member_ban(event):
    try:
        for channel in event.guild.channels:
            c = bot.logs_from(channel, limit=200000)
            async for message in c:
                if message.author == event.user:
                    message.delete()
    except:
        pass

@bot.command(pass_context=True)
async def dump(rx):
    try:
        if rx.message.author.permissions_in(rx.message.channel).administrator or rx.message.author.id == "119094696487288833":
            i = 0
            c = bot.logs_from(rx.message.channel, limit=100000)
            await bot.say("Queueing images...")
            entries = ""
            async for message in c:
                if message.author.bot:
                    continue
                elif message.attachments:
                    url = message.attachments[0]["url"]
                    entries += "{} {} {}\n".format(url, message.channel.id, message.id)
                    i += 1
                else:
                    pass
            with open("queue", "a") as fp:
                fp.write(entries)
                fp.close()
            await bot.say("Queued {} images.".format(i))
            i = 0
            c = bot.logs_from(rx.message.channel, limit=100000)
            await bot.say("Downloading text...")
            file = open("logs/{}.txt".format(rx.message.channel.id), "w")
            async for message in c:
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
            await bot.say("Collected {} lines of text.".format(i))
        else:
            await bot.say("Administrator only.")
    except:
        pass


@bot.command(pass_context=True)
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
                await bot.say(quotes)
            except:
                await bot.say("Awoo... an error has occurred.")
        elif os.path.exists("logs/{}.txt".format(rx.message.channel.id)):
            fp = open("logs/{}.txt".format(rx.message.channel.id), "r")
            log = fp.readlines()
            fp.close()
            for i in range(limit):
                quotes += random.choice(log)
            try:
                await bot.say(quotes)
            except:
                await bot.say("Awoo... an error has occurred.")
        else:
            await bot.say("Awoo... this channel has not been dumped.")
    except KeyError:
        await bot.say("Awoo... this channel has not been dumped.")

def rl_inBot(rx):
    try:
        if logs[rx.message.channel.id]:
            return random.choice(logs[rx.message.channel.id])
        elif os.path.exists("logs/{}.txt".format(rx.message.channel.id)):
            fp = open("logs/{}.txt".format(rx.message.channel.id), "r")
            log = fp.readlines()
            fp.close()
            return random.choice(log)
        else:
            return "Awoo... this channel has not been dumped."
    except KeyError:
        return "Awoo... this channel has not been dumped."

@bot.command(pass_context=True)
async def rt(rx):
    try:
        if logs[rx.message.channel.id]:
            text = "".join(logs[rx.message.channel.id])
        elif os.path.exists("logs/{}.txt".format(rx.message.channel.id)):
            fp = open("logs/{}.txt".format(rx.message.channel.id), "r")
            text = fp.read()
            fp.close()
        else:
            await bot.say("Awoo... this channel has not been dumped.")
        try:
            samples = int(rx.message.content.split(' ')[1])
            if samples > 2000:
                samples = 2000
        except:
            samples = 200
        await bot.say(markovify.Text(text).make_short_sentence(samples))
    except KeyError:
        await bot.say("Awoo... this channel has not been dumped.")

@bot.command(pass_context=True)
async def ri(rx):
    directory = str(rx.message.channel.id)
    file = "{}/{}".format(directory, random.choice(os.listdir(directory)))
    try:
        await bot.send_file(rx.message.channel, file, content=rl_inBot(rx))
    except:
        print("File '{}' not found.".format(file))

@bot.command(pass_context=True)
async def rp(rx):
    names = []
    for member in rx.message.server.members:
        names.append(member.name)
    text1 = rl_inBot(rx)
    text2 = rl_inBot(rx)
    name1 = random.choice(names)
    name2 = random.choice(names)
    if name1 == name2:
        final = "{}: {}\nalso {}: {}".format(name1, text1, name2, text2)
    else:
        final = "{}: {}\n{}: {}".format(name1, text1, name2, text2)
    await bot.say(final)

@bot.command(pass_context=True)
async def setP(rx):
    if rx.message.author.id == "119094696487288833":
        await bot.change_presence(game=discord.Game(name=rx.message.content[6:]))

bot.change_presence(game=discord.Game(name=".jhelp for help"))
bot.run("[REDACTED]")
