#!/usr/bin/python -u
import discord
from discord.ext import commands
import asyncio
import os
import random
import markovify
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
owner = 119094696487288833
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", owner_id=owner, intents=intents)

@bot.event
async def on_ready():
    print(f"I am running on {bot.user.name} with the ID {bot.user.id}")
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="you."))

@bot.command()
async def verify_count(rx):
    valid_channel_names = ["counting"]
    try:
        if rx.author.permissions_in(rx.message.channel).administrator or rx.author.id == owner:
            if rx.message.channel.name not in valid_channel_names:
                await rx.author.send(f"Cannot test in a non-counting channel. Channel name: '{rx.message.channel.name}'.\n" +
                                     "Change the channel name to '#counting' or edit the allowed names in bot.py.")
                return
            test_log = ""
            await rx.author.send("Starting counting channel tests.")
            await rx.message.delete()
            c = await rx.message.channel.history(limit=None).flatten()
            c.reverse()
            mistake_offset = 0
            async with rx.message.channel.typing():
                for pos, message in enumerate(c[:-1], start=1):
                    try:
                        body = int(message.content)
                    except ValueError as verr:
                        test_log += f"Error at message {message.author}:\"{message.content}\", position {pos}: Non-integer\n"
                        body = pos
                    if body != pos + mistake_offset:
                        test_log += f"Error at message {message.author}:\"{message.content}\", position {pos}: Text order mismatch\n"
                        mistake_offset = (body - pos)
                    if message.author == c[pos].author:
                        test_log += f"Error at message {c[pos].author}:\"{c[pos].content}\", position {pos+1}: Double posting\n"
            await rx.author.send(f"Errors found:\n{test_log}")
        else:
            await rx.author.send("Administrator only.")
    except Exception as e:
        print(str(e))

@bot.command()
async def dump(rx):
    try:
        if rx.author.permissions_in(rx.message.channel).administrator or rx.author.id == owner:
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
    elif rx.author.permissions_in(rx.message.channel).administrator or rx.author.id == owner:
        pass
    else:
        await rx.send("You are not allowed to collect from other members.")
        return
    try:
        print(f"Now collecting messages for {str(user)} ({user.id})")
        guild_path = Path(f"user/{rx.message.guild.id}")
        if not guild_path.exists():
            guild_path.mkdir()
        file = open(f"user/{rx.message.guild.id}/{user.id}.txt", "w")
        await rx.send("Collecting messages... (this can take up to an hour!)")
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
        await rx.send(f"Messages collected for {str(user)}.")
        fp = open(f"user/{rx.message.guild.id}/{user.id}", "r")
        users[user.id] = fp.readlines()
        fp.close()
    except:
        pass

@collect.error
async def collect_error(rx, error):
    if isinstance(error, commands.BadArgument):
        await rx.send("Awoo... user not found.")

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
        quotes += get_random_quote(rx.channel.id)
    await rx.send(quotes)

def get_random_quote(channel):
    try:
        if guilds[channel]:
            return random.choice(guilds[channel])
    except KeyError:
        if os.path.exists(f"guild/{channel}.txt"):
            fp = open(f"guild/{channel}.txt", "r")
            log = fp.readlines()
            fp.close()
            return random.choice(log)
        else:
            return "Awoo... this channel has not been dumped."

@bot.command()
async def rv(rx):
    voice_channel = rx.author.voice
    author_activity = rx.author.activity
    joinable = False; users = []
    if not voice_channel:
        await rx.send("Awoo... you are not in a voice channel."); return
    else:
        guild_vcs = rx.guild.voice_channels
        for guild_member in rx.guild.members:
            if guild_member.voice:
                users.append(guild_member)
        for guild_vc in guild_vcs:
            if rx.me.permissions_in(guild_vc).connect:
                joinable = True; break
        if joinable == False:
            await rx.send("Awoo... I don't have permission to do that."); return
        for user in users:
            while True:
                random_vc = random.choice(guild_vcs)
                if rx.me.permissions_in(random_vc).connect:
                    break
            await user.move_to(random_vc)

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
        await rx.send(markovify.Text(text).make_short_sentence(250))

@rm.error
async def rm_error(rx, error):
    if isinstance(error, commands.BadArgument):
        await rx.send("Awoo... user not found.")

@bot.command()
async def rt(rx, *max_chars):
    try:
        if max_chars:
            if int(max_chars[0]) > 2000:
                max_chars = 2000
            else:
                max_chars = int(max_chars[0])
        else:
            max_chars = 200
    except ValueError:
        max_chars = 200
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
        await rx.send(markovify.Text(text).make_short_sentence(max_chars))

@bot.command()
async def ri(rx, *, channel: discord.TextChannel=-1):
    if channel == -1:
        channel = rx.channel.id
    else:
        channel = channel.id
    directory = "guild/" + str(channel)
    image = random.choice(os.listdir(directory))
    file = f"{directory}/{image}"
    boring = {".ri", ".rl", ".rt", "t!help", "t!slots"}
    while True:
        message = get_random_quote(channel)
        if message not in boring:
            break
    try:
        await rx.send(file=discord.File(file), content=message)
    except:
        print(f"File '{file}' not accessible.")

@ri.error
async def ri_error(rx, error):
    if isinstance(error, commands.BadArgument):
        await rx.send("Awoo... channel not found.")

@bot.command()
async def rp(rx):
    names = []
    for member in rx.guild.members:
        names.append(member.name)
    text1 = get_random_quote(rx.channel.id)
    text2 = get_random_quote(rx.channel.id)
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
