import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import os
import random
import markovify
from pathlib import Path
from urltest import downloadTxt

bot = commands.Bot(command_prefix=".")

@bot.event
async def on_ready():
    print("I am running on " + bot.user.name)
    print("with the ID " + bot.user.id)

@bot.command(pass_context=True)
async def ping(rx):
    await bot.say(":ping_pong: pong!! xSSS")
    print("user has pinged")

@bot.command(pass_context=True)
async def info(rx, user: discord.Member):
    await bot.say("The users name is: {}".format(user.name))
    await bot.say("The users ID is: {}".format(user.id))
    await bot.say("The users status is: {}".format(user.status))
    await bot.say("The users highest role is: {}".format(user.top_role))
    await bot.say("The user joined at: {}".format(user.joined_at))

@bot.command(pass_context=True)
async def kick(rx, user: discord.Member):
    await bot.say(":boot: Cya, {}. Ya loser!".format(user.name))
    await bot.kick(user)

@bot.command(pass_context=True)
async def dump(rx):
    try:
        #await bot.say(str(rx.message.channel.name))
        if rx.message.author.id == "119094696487288833":
            i = 0
            try:
                c = bot.logs_from(rx.message.channel, limit=int(rx.message.content.split(' ')[1]))
                print(int(rx.message.content.split(' ')[1]))
            except:
                c = bot.logs_from(rx.message.channel, limit=10)
            if not os.path.exists("logs"):
                os.makedirs("logs")
            filename = "logs\\" + "discLogs_" + rx.message.channel.name + ".txt"
            file = open(filename, 'w')
            async for message in c:
                try:
                    url = message.attachments[0]['url']
                    file.write(url + "\n")
                    i+=1
                except:
                    pass
            file.close()
            #await bot.say("done: " + str(i) + " pictures dumped to txt in: " + "\\" + "logs\\" + "discLogs_" + rx.message.channel.name + ".txt")
            await bot.say("downloading...")
            downloadTxt(filename, rx.message.channel.name)
            #await bot.say("done downloading to \\" + rx.message.channel.name)
            await bot.say("done downloading " + str(i) + " channel images.")
        else:
            await bot.say("sorry, not for u. :cry:")
            print("someone not u tried to use dumpPics")
    except:
        pass

@bot.command(pass_context=True)
async def dump_text(rx):
    try:
        #await bot.say(str(rx.message.channel.name))
        if rx.message.author.id == "119094696487288833":
            i = 0
            try:
                c = bot.logs_from(rx.message.channel, limit=int(rx.message.content.split(' ')[1]))
                print(int(rx.message.content.split(' ')[1]))
            except:
                c = bot.logs_from(rx.message.channel, limit=10)
            if not os.path.exists("logs"):
                os.makedirs("logs")
            filename = "logs\\" + "discLogs_Text_" + rx.message.channel.name + ".txt"
            await bot.say("logging... :gun: pew pew pew haha")
            file = open(filename, 'w')
            async for message in c:
                try:
                    url = message.content
                    if url == "":
                        continue
                    else:
                        file.write(url + "\n")
                        i += 1
                except:
                    pass
            file.close()
            await bot.say("collected " + str(i) + " lines of text")
        else:
            await bot.say("sorry, not for u. :cry:")
            print("someone not u tried to use dumpPics")
    except:
        pass

@bot.command(pass_context=True)
async def rl(rx):
    try:
        #cname = rx.message.channel.name
        CC_add = "logs\\" + "discLogs_Text_" + rx.message.channel.name + ".txt"
        ccF = open(CC_add, 'r')
        CC = ccF.readlines()  # global
        ccF.close()
    except:
        print("loading CC list failed... check file name/dir")
        CC = ["u shouldnt see this.. :gun: "]
    try:
        limit = int(rx.message.content.split(' ')[1])
        if limit > 10:
            limit = 10
    except:
        limit=1
    texts = ""
    for i in range(limit):
        texts += random.choice(CC)
        texts += "\n"
    try:
        await bot.say(texts)
    except:
        pass

def rl_inBot(rx, twoLine = False):
    try:
        CC_add = "logs\\" + "discLogs_Text_" + rx.message.channel.name + ".txt"
        ccF = open(CC_add, 'r')
        CC = ccF.readlines()  # global
        ccF.close()
    except:
        print("loading CC list failed... check file name/dir")
        CC = ["nah"]
    print(len(CC))
    if twoLine == True:
        texts = ""
        texts2 = ""
        spot = random.randint(1, len(CC) - 1)
        texts += CC[spot]
        texts2 += CC[spot+1]
        return texts, texts2
    else:
        texts = ""
        texts += random.choice(CC)
        return texts

@bot.command(pass_context=True)
async def rt(rx):
    CC_add = "logs\\" + "discLogs_Text_correctchat.txt"
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
    try:
        CC_add = "logs\\" + "discLogs_Text_" + rx.message.channel.name + ".txt"
        ccF = open(CC_add, 'r')
        CC = ccF.readlines()  # global
        ccF.close()
    except:
        #print("loading CC list failed... check file name/dir")
        CC = ["if u see this message joey fucked up"]

    ext = [".jpg",".png",".gif",".jpeg"]
    folderPath = rx.message.channel.name
    file_count = len(os.listdir(folderPath))
    randFilePart = "000" + str(random.randint(1,file_count))
    file = os.path.join(folderPath, randFilePart)
    files = [file + extIterated for extIterated in ext]
    for fileIt in files:
        path = Path(fileIt)
        if path.exists():
            await bot.send_file(rx.message.channel, fileIt, content=rl_inBot(rx))
        else:
            #print(fileIt + " does not exist")
            pass

@bot.command(pass_context=True)
async def rp(rx):
    print("rp running")
    names = ["bean","joey","jacob","nick","godfrey","steven","derek","kyle tamondong","roman","ben cimperman","anna","grant","jimmy","cole","max","dylan","kash","ian","will",
    "skyler","kevin","charlie","ayush","derek","sam","asstumpy","jackson","jackson koenig","matt","sammy","taylor","oneassen","mumble mom","max haland","jon","mike warner",
    "bartleby","himsel","dion a", "one half assen", "johnny", "johnny silktouch", "martin smith","charles terzian","justin","vishnu","hunter","murder black teen","nick barone",
    "kevin roland","dennis","sebastian","neetorin","cole","brad","texascole","fourchan","ran","ryne","colten","nebuchadnezzar","cody","wills parents"]
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
    await bot.say("Like Succk on Facebook https://www.facebook.com/makesucckgreatagain/")

@bot.command(pass_context=True)
async def ro(rx):
    await bot.say(" grant u dumapss its dotrp not ro u musta mispress interestinf :gun:")

@bot.command(pass_context=True)
async def jhelp(rx):
    await bot.say(".rl, .rt, .ri, .rp. ||| .joey, .steveo, .grant, .jacob ||| .p, .succk ||| [backend only] .dump, dump_text, .setP")

@bot.command(pass_context=True)
async def setP(rx):
    if rx.message.author.id == "119094696487288833":
        await bot.change_presence(game=discord.Game(name=rx.message.content))

bot.change_presence(game=discord.Game(name=".jhelp for help"))
bot.run("[REDACTED]")
