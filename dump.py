import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import os
import requests
from pathlib import Path

async def dumper(rx, client):
    bot = client
    try:
        if rx.message.author.permissions_in(rx.message.channel).administrator:
            try:
                if rx.message.content.split(" ")[1] == "--skip-imgs":
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
                    pass
            except:
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
                            if os.path.isfile("{}/{}.{}".format(rx.message.channel.id, message.id, ext)):
                                i += 1
                                if i % 100 == 0:
                                    print("Downloaded {} images.".format(i))
                                continue
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
