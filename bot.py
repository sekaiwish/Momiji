import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import os
import random
import markovify
import requests
from pathlib import Path
from urltest import downloadTxt

bot = commands.Bot(command_prefix=".")

if not os.path.exists("logs"):
    os.makedirs("logs")
logs = {}
logFiles = os.listdir("logs")
for log in range(0, len(logFiles)):
    fp = open("logs/{}".format(logFiles[log]), "r")
    logFile = logFiles[log][:-4]
    logs[logFile] = fp.readlines()
    fp.close()

@bot.event
async def on_ready():
    print("I am running on {}\nwith the ID {}".format(bot.user.name, bot.user.id))

@bot.command(pass_context=True)
async def ping(rx):
    await bot.say(":ping_pong: pong!! xSSS")
    print("user has pinged")

@bot.command(pass_context=True)
async def dump(rx):
    try:
        if rx.message.author.permissions_in(rx.message.channel).administrator:
            if not os.path.exists(rx.message.channel.id):
                os.makedirs(rx.message.channel.id)
            i = 0
            c = bot.logs_from(rx.message.channel, limit=100000)
            await bot.say("Downloading images...")
            async for message in c:
                if message.author.bot:
                    pass
                elif message.attachments:
                    try:
                        url = message.attachments[0]["url"]
                        ext = message.attachments[0]["filename"].split(".")[-1]
                        r = requests.get(message.attachments[0]["url"], stream=True)
                        with open("{}/{}.{}".format(rx.message.channel.id, message.id, ext), "wb") as fd:
                            for chunk in r.iter_content(chunk_size=128):
                                fd.write(chunk)
                        i += 1
                        if i % 100 == 0:
                            print("Downloaded {} images.".format(i))
                    except:
                        pass
                else:
                    pass
            await bot.say("Collected {} images.".format(i))
            i = 0
            c = bot.logs_from(rx.message.channel, limit=100000)
            await bot.say("Downloading text...")
            file = open("logs/{}.txt".format(rx.message.channel.id), "w")
            async for message in c:
                m = message.clean_content
                if m == "":
                    pass
                elif message.author.bot:
                    pass
                else:
                    file.write(m + "\n")
                    i += 1
                    if i % 1000 == 0:
                        print("Downloaded {} lines.".format(str(i)))
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
                await bot.say("i made a fucky wucky")
        elif os.path.exists("logs/{}.txt".format(rx.message.channel.id)):
            fp = open("logs/{}.txt".format(rx.message.channel.id), "r")
            log = fp.readlines()
            fp.close()
            for i in range(limit):
                quotes += random.choice(log[rx.message.channel.id])
            try:
                await bot.say(quotes)
            except:
                await bot.say("i made a fucky wucky")
        else:
            await bot.say("your channel isnt a dump")
    except KeyError:
        await bot.say("your channel isnt a dump")

def rl_inBot(rx):
    try:
        if logs[rx.message.channel.id]:
            return random.choice(logs[rx.message.channel.id])
        elif os.path.exists("logs/{}.txt".format(rx.message.channel.id)):
            fp = open("logs/{}.txt".format(rx.message.channel.id), "r")
            log = fp.readlines()
            fp.close()
            return random.choice(log[rx.message.channel.id])
        else:
            return "your channel isnt a dump"
    except KeyError:
        return "your channel isnt a dump"

@bot.command(pass_context=True)
async def rt(rx):
    CC_add = "logs/{}.txt".format(rx.message.channel.id)
    with open(CC_add) as f:
        text = f.read()
    text_model = markovify.Text(text)
    try:
        lengthIn = int(rx.message.content.split(' ')[1])
        if lengthIn > 2000:
            limit = 2000
    except:
        lengthIn = 200

    line = text_model.make_short_sentence(lengthIn)
    await bot.say(line)

@bot.command(pass_context=True)
async def ri(rx):
    directory = rx.message.channel.id
    file = "{}/{}".format(directory, random.choice(os.listdir(directory)))
    try:
        await bot.send_file(rx.message.channel, file, content=rl_inBot(rx))
    except:
        print("File '{}' not found.".format(file))

@bot.command(pass_context=True)
async def rp(rx):
    if rx.message.server.id == "225424272825384960":
        names = ["bean","joey","jacob","nick","godfrey","steven","derek","kyle tamondong","roman","ben cimperman","anna","grant","jimmy","cole","max","dylan","kash","ian","will",
        "skyler","kevin","charlie","ayush","derek","sam","asstumpy","jackson","jackson koenig","matt","sammy","taylor","oneassen","mumble mom","max haland","jon","mike warner",
        "bartleby","himsel","dion a","one half assen","johnny","johnny silktouch","martin smith","charles terzian","justin","vishnu","hunter","murder black teen","nick barone",
        "kevin roland","dennis","sebastian","neetorin","cole","brad","texascole","fourchan","ran","ryne","colten","nebuchadnezzar","cody","wills parents"]
    else:
        names = []
        for member in rx.message.server.members:
            names.append(member.name)
    text1 = rl_inBot(rx)
    text2 = rl_inBot(rx)
    name1 = random.choice(names)
    name2 = random.choice(names)
    final = ""
    if name1 == name2:
        final += name1 + ": " + text1 + "\n" + "also " + name2 + " : " + text2
    else:
        final += name1 + ": " + text1 + "\n" + name2 + " : " + text2
    await bot.say(final)

@bot.command(pass_context=True)
async def grant(rx):
    if rx.message.author.id == "160624126480875520":
        await bot.say("ah yes me too grant")
    else:
        await bot.say("sorry....... kid,,,..")

@bot.command(pass_context=True)
async def jacob(rx):
    if rx.message.author.id == "214450788326440961":
        await bot.say("planes vRRRRROoom")
    else:
        await bot.say("nah nigga")

@bot.command(pass_context=True)
async def p(rx):
    await bot.say("this command is depreciated :gun: ass Hole :gun: gun:")

@bot.command(pass_context=True)
async def steveo(rx):
    if rx.message.author.id == "119094696487288833":
        await bot.say("java scripyt")
    else:
        await bot.say("sorr. y nah")

@bot.command(pass_context=True)
async def kash(rx):
    if rx.message.author.id == "221067695964028929":
        await bot.say("when i die bury me inside a gucci coffin")
    else:
        await bot.say("u dont deserve kash buddy")

@bot.command(pass_context=True)
async def ayush(rx):
    if rx.message.author.id == "116668711414398978":
        await bot.say("hahah yyyeaahhhh")
    else:
        await bot.say("haha wait")

@bot.command(pass_context=True)
async def joey(rx):
    if rx.message.author.id == "133784395612946432":
        await bot.say("path of, esile")
    else:
        await bot.say("its a shame bc i coded this for myself so its like nobody can even see what it says for me unless i show them anyways...")

@bot.command(pass_context=True)
async def succk(rx):
    await bot.say("Like Succk on Facebook https://www.facebook.com/bigsucck/")

@bot.command(pass_context=True)
async def ro(rx):
    await bot.say(" grant u dumapss its dotrp not ro u musta mispress interestinf :gun:")

@bot.command(pass_context=True)
async def jhelp(rx):
    await bot.say(".rl, .rt, .ri, .rp. ||| .joey, .steveo, .grant, .jacob ||| .p, .succk ||| [backend only] .dump, dump_text, .setP")

@bot.command(pass_context=True)
async def setP(rx):
    if rx.message.author.id == "119094696487288833":
        await bot.change_presence(game=discord.Game(name=rx.message.content[6:]))

bot.change_presence(game=discord.Game(name=".jhelp for help"))
bot.run("[REDACTED]")
