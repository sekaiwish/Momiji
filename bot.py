import discord
from discord.ext import commands
import asyncio
import os
import random
import markovify
import typing
from subprocess import Popen
from pathlib import Path

# Startup/Setup
if os.path.exists("token"):
    print("Using existing token")
    with open("token", "r") as fp:
        token = fp.read()
else:
    token = input("Token: ")
    with open("token", "w") as fp:
        fp.write(token)
if not os.path.exists("queue"):
    Path("queue").touch()
guild_path = Path("./guild")
if not guild_path.exists():
    guild_path.mkdir()
user_path = Path("./user")
if not user_path.exists():
    user_path.mkdir()
verify_path = Path("./verify")
if not verify_path.exists():
    verify_path.mkdir()
guilds = {}
for guild in os.scandir("guild"):
    if guild.is_file():
        fp = open(f"guild/{guild.name}", "r")
        guild_id = int(guild.name[:-4])
        guilds[guild_id] = fp.readlines()
        fp.close()
users = {}
for guild in os.scandir("user"):
    for user in os.scandir(guild):
        fp = open(f"user/{guild.name}/{user.name}", "r")
        user_id = int(user.name[:-4])
        users[int(guild.name)] = {}
        users[int(guild.name)][user_id] = fp.readlines()
        fp.close()

# Initialise dumping queue
#devnull = open(os.devnull, "wb")
Popen(["python", "dumpqueue.py"])

bot = commands.Bot(command_prefix=";", owner_id=119094696487288833)

@bot.event
async def on_ready():
    print(f"I am running on {bot.user.name} with the ID {bot.user.id}")
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="you."))

@bot.command()
async def dump(rx):
    try:
        if rx.author.permissions_in(rx.message.channel).administrator or rx.author.id == 119094696487288833:
            i = 0
            await rx.send("Scanning channel...")
            c = await rx.message.channel.history(limit=None).flatten()
            async with rx.message.channel.typing():
                entries = ""
                for message in c:
                    if message.author.bot:
                        continue
                    elif message.attachments:
                        for a in message.attachments:
                            entries += f"{a.url} {message.channel.id} {message.id}\n"
                            i += 1
                with open("queue", "a") as fp:
                    fp.write(entries)
                    fp.close()
                await rx.send(f"Queued {i} images.")
            i = 0
            async with rx.message.channel.typing():
                file = open(f"guild/{rx.message.channel.id}.txt", "w")
                for message in c:
                    m = message.content
                    if m == "":
                        continue
                    elif message.author.bot:
                        continue
                    else:
                        file.write(m + "\n")
                        i += 1
                file.close()
                await rx.send(f"Collected {i} lines of text.")
            log = str(rx.message.channel.id) + ".txt"
            fp = open(f"guild/{log}", "r")
            guilds[rx.message.channel.id] = fp.readlines()
            fp.close()
        else:
            await rx.send("Administrator only.")
    except:
        pass

@bot.command()
async def collect(rx, *, user: discord.Member=-1):
    if user == -1:
        user = rx.author
    elif rx.author.permissions_in(rx.message.channel).administrator or rx.author.id == 119094696487288833:
        pass
    else:
        await rx.send("You are not allowed to collect from other members.")
    try:
        print(f"Now collecting messages for {str(user)} ({user.id})")
        guild_path = Path(f"user/{rx.message.guild.id}")
        if not guild_path.exists():
            guild_path.mkdir()
        file = open(f"user/{rx.message.guild.id}/{user.id}.txt", "w")
        await rx.send("Collecting messages...")
        for channel in rx.guild.text_channels:
            if channel.permissions_for(rx.message.guild.me).read_message_history:
                async for message in channel.history(limit=None):
                    if message.author.id == user.id:
                        m = message.content
                        if m == "":
                            continue
                        else:
                            file.write(f"{m}\n")
        file.close()
        await rx.send("Messages collected.")
        fp = open(f"user/{rx.message.guild.id}/{user.id}", "r")
        users[user.id] = fp.readlines()
        fp.close()
    except:
        pass

@bot.command()
async def rl(rx, *limit):
    try:
        if limit:
            if int(limit[0]) > 15:
                limit = 15
            else:
                limit = int(limit[0])
        else:
            limit = 1
    except ValueError:
        limit = 1
    quotes = ""
    for i in range(limit):
        quotes += get_random_quote(rx)
    await rx.send(quotes)

def get_random_quote(rx):
    try:
        if guilds[rx.message.channel.id]:
            return random.choice(guilds[rx.message.channel.id])
    except KeyError:
        if os.path.exists(f"guild/{rx.message.channel.id}.txt"):
            fp = open(f"guild/{rx.message.channel.id}.txt", "r")
            log = fp.readlines()
            fp.close()
            return random.choice(log)
        else:
            return "Awoo... this channel has not been dumped."

@bot.command()
async def rm(rx, *, user: discord.Member=-1):
    if user == -1:
        user = rx.author
    try:
        if users[rx.message.guild.id][user.id]:
            text = "".join(users[rx.message.guild.id][user.id])
    except KeyError:
        if os.path.exists(f"user/{rx.message.guild.id}/{user.id}.txt"):
            fp = open(f"user/{rx.message.guild.id}/{user.id}.txt", "r")
            text = fp.read()
            fp.close()
        else:
            await rx.send("Awoo... this user has not been researched.")
    if text:
        await rx.send(markovify.Text(text).make_sentence())

@rm.error
async def rm_error(rx, error):
    if isinstance(error, commands.BadArgument):
        await rx.send("Awoo... user not found.")

@bot.command()
async def rt(rx, *samples):
    try:
        if samples:
            if int(samples[0]) > 2000:
                samples = 2000
            else:
                samples = int(samples[0])
        else:
            samples = 200
    except ValueError:
        samples = 200
    try:
        if guilds[rx.message.channel.id]:
            text = "".join(guilds[rx.message.channel.id])
    except KeyError:
        if os.path.exists(f"guild/{rx.message.channel.id}.txt"):
            fp = open(f"guild/{rx.message.channel.id}.txt", "r")
            text = fp.read()
            fp.close()
        else:
            await rx.send("Awoo... this channel has not been dumped.")
    if text:
        await rx.send(markovify.Text(text).make_short_sentence(samples))

@bot.command()
async def ri(rx):
    directory = str(rx.message.channel.id)
    image = random.choice(os.listdir(directory))
    file = f"guild/{directory}/{image}"
    boring = {".ri", ".rl", ".rt", "t!help", "t!slots"}
    while True:
        message = get_random_quote(rx)
        if message not in boring:
            break
    try:
        await rx.send(file=discord.File(file), content=message)
    except:
        print(f"File '{file}' not accessible.")

@bot.command()
async def rp(rx):
    names = []
    for member in rx.guild.members:
        names.append(member.name)
    text1 = get_random_quote(rx)
    text2 = get_random_quote(rx)
    name1 = random.choice(names)
    name2 = random.choice(names)
    if name1 == name2:
        final = f"{name1}: {text1}\nalso {name2}: {text2}"
    else:
        final = f"{name1}: {text1}\n{name2}: {text2}"
    await rx.send(final)

@bot.command()
async def verify(rx):
    image = random.choice(os.listdir("verify"))
    file = f"verify/{image}"
    try:
        await rx.send(file=discord.File(file))
    except:
        print(f"File '{file}' not accessible.")

bot.run(token)
