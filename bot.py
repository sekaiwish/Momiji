#!/usr/bin/python -u
import os, time, random, threading, asyncio, pickle, requests, markovify, discord
from discord.ext import commands
from classes import Message, QueuedFile, Responses

channels = {}
owner = 119094696487288833
intents = discord.Intents.none()
intents.guilds = True; intents.members = True; intents.voice_states = True; intents.guild_messages = True
bot = commands.Bot(command_prefix='.', owner_id=owner, intents=intents)
responses = Responses()

def load(file):
    with open(file, 'rb') as fp:
        data = pickle.load(fp)
        fp.close()
        return data
def save(file, data):
    with open(file, 'wb') as fp:
        pickle.dump(data, fp)
def setup_files(*files):
    for file in files:
        if not os.path.isfile(file):
            if os.path.exists(file): raise Exception('Require file exists as dir')
            f = open(file, 'x')
def setup_dirs(*dirs):
    for dir in dirs:
        if not os.path.isdir(dir):
            if os.path.exists(dir): raise Exception('Required dir exists as file')
            os.mkdir(dir)
setup_files('token')
setup_dirs('files', 'messages', 'queue', 'verify')
with open('token', 'r+') as fp:
    if not fp.read():
        token = input('Token: ')
        fp.write(token)
    else:
        fp.seek(0); token = fp.read()
        print('Using existing token')
for channel in os.scandir('messages'):
    channels[int(channel.name)] = load(f'messages/{channel.name}')

def dump_queue():
    valid = {'png', 'jpg', 'jpeg', 'gif', 'webm', 'mov', 'mp4'}
    while True:
        queues = [f for f in os.scandir('queue')]
        queues.sort(key=lambda x: os.path.getctime(x))
        if queues:
            while True:
                queue = f'{queues[0].path}'
                data = load(queue)
                if data == set():
                    os.remove(queue); print(f'Image dump for {queues[0].name} finished'); break
                download = data.pop()
                save(queue, data)
                extension = download.url.split('.')[-1]
                if os.path.exists(f'files/{download.id}.{extension}'): continue
                if extension in valid:
                    r = requests.get(download.url, stream=True)
                    with open(f'files/{download.id}.{extension}', 'wb') as fd:
                        for chunk in r.iter_content(chunk_size=128): fd.write(chunk)
        else: time.sleep(1)

def random_quote(channel):
    boring = {'', '.ri', '.rl', '.rt', '.rm', 't!help', 't!slots'}
    while True:
        message = random.choice(tuple(channels[channel])).body
        if message not in boring: return message

def random_image(channel):
    while True:
        message = random.choice(tuple(channels[channel]))
        # will infinite loop if no messages with image
        if message.attachments:
            return random.choice(tuple(message.attachments))

def guild_dumped(guild):
    for channel in guild.text_channels:
        if channel.id in channels: return True
    return False

def channel_dumped(channel):
    if channel.id in channels: return True
    else: return False

@bot.command()
async def dump(rx):
    try:
        if rx.author.guild_permissions.administrator or rx.author.id == owner:
            print(f'Dump started ({rx.guild.name}, {rx.channel.name})')
            i = 0; j = 0; messages = set(); files = set(); last_message = None
            if rx.channel.id in channels:
                timestamps = [m.timestamp for m in channels[rx.channel.id]]
                timestamps.sort()
                last_message = timestamps[-1]
            await rx.send('Scanning channel...')
            if last_message: c = await rx.history(limit=None, after=last_message).flatten()
            else: c = await rx.history(limit=None).flatten()
            async with rx.channel.typing():
                for message in c:
                    if message.author.bot: continue
                    attachments = set()
                    for attachment in message.attachments:
                        extension = attachment.url.split('.')[-1]
                        attachments.add(f'{attachment.id}.{extension}')
                        files.add(QueuedFile(attachment.url, message.channel.id, attachment.id))
                        j += 1
                    messages.add(Message(message.content, message.author.id, message.created_at, attachments))
                    i += 1
            if last_message: messages = messages.union(channels[rx.channel.id])
            save(f'messages/{rx.channel.id}', messages)
            save(f'queue/{rx.channel.id}', files)
            queue = len(os.listdir('queue'))
            await rx.message.reply(f'Collected {i} messages, queued {j} images. (#{queue} in queue)')
            channels[rx.channel.id] = messages
            print(f'Dump finished ({rx.guild.name}, {rx.channel.name})')
        else:
            await rx.message.reply(responses.no_permission)
    except:
        print(f'Dump failed ({rx.guild.name}, {rx.channel.name})')

@bot.command()
async def rs(rx):
    if not guild_dumped(rx.guild):
        await rx.message.reply(responses.guild_not_dumped); return
    tracked = []; messages = 0; text = ''; members_msg = {}; members_char = {}
    for channel in rx.guild.text_channels:
        if channel.id in channels:
            tracked.append(channel.name)
            for m in channels[channel.id]:
                text += m.body; messages += 1
                if m.author in members_msg:
                    members_msg[m.author] += 1; members_char[m.author] += len(m.body)
                else:
                    members_msg[m.author] = 1; members_char[m.author] = len(m.body)
    msg_id = max(members_msg, key=members_msg.get)
    char_id = max(members_char, key=members_char.get)
    msg_name = await bot.fetch_user(msg_id); char_name = await bot.fetch_user(char_id)
    embed=discord.Embed(title=f'Statistics for {rx.guild.name}'); embed.set_thumbnail(url=rx.guild.icon_url)
    embed.add_field(name='Tracked Channels', value=tracked, inline=True)
    embed.add_field(name='Number of Messages', value=f'{messages:,}', inline=True)
    embed.add_field(name='Number of Characters', value=f'{len(text):,}', inline=True)
    embed.add_field(name='Most messages sent', value=f'{msg_name} ({members_msg[msg_id]:,})', inline=True)
    embed.add_field(name='Most characters sent', value=f'{char_name} ({members_char[char_id]:,})', inline=True)
    await rx.message.reply(embed=embed)

@bot.command()
async def rl(rx, limit=1):
    if not channel_dumped(rx.channel):
        await rx.message.reply(responses.channel_not_dumped); return
    if limit > 15: limit = 15
    quotes = ''
    for i in range(limit): quotes += f'{random_quote(rx.channel.id)}\n'
    await rx.message.reply(quotes)

@bot.command()
async def ri(rx, channel: discord.TextChannel=None):
    if channel == None: channel = rx.channel.id
    else: channel = channel.id
    if not channel_dumped(rx.channel):
        await rx.message.reply(responses.channel_not_dumped); return
    if os.path.exists(f'queue/{channel}'):
        await rx.message.reply(responses.channel_dumping); return
    file = f'files/{random_image(channel)}'
    await rx.message.reply(file=discord.File(file), content=random_quote(channel))

@bot.command()
async def rt(rx, max=200):
    if max > 2000: max = 2000
    if not guild_dumped(rx.guild):
        await rx.message.reply(responses.guild_not_dumped); return
    text = ''
    for gc in rx.guild.text_channels:
        if gc.id in channels: text += ' '.join([m.body for m in channels[gc.id]])
    await rx.message.reply(markovify.Text(text).make_sentence(tries=50))

@bot.command()
async def rm(rx, user: discord.Member=None):
    if user == None: user = rx.author.id
    else: user = user.id
    if not guild_dumped(rx.guild):
        await rx.message.reply(responses.guild_not_dumped); return
    boring = {'', '.ri', '.rl', '.rt', '.rm', 't!help', 't!slots'}
    text = ''
    for gc in rx.guild.text_channels:
        if gc.id in channels: text += ' '.join([m.body if (m.author == user and m.body not in boring) else '' for m in channels[gc.id]])
    await rx.message.reply(markovify.Text(text).make_sentence(tries=50))

@bot.command()
async def rp(rx):
    if not channel_dumped:
        await rx.message.reply(responses.channel_not_dumped); return
    names = random.choices([m.display_name for m in rx.guild.members], k=2)
    if names[0] == names[1]:
        await rx.message.reply(f'{names[0]}: {random_quote(rx.channel.id)}\nalso {names[1]}: {random_quote(rx.channel.id)}')
    else:
        await rx.message.reply(f'{names[0]}: {random_quote(rx.channel.id)}\n{names[1]}: {random_quote(rx.channel.id)}')

@bot.command()
async def rv(rx):
    if not rx.author.voice:
        await rx.message.reply(responses.no_voice_channel); return
    joinable = False
    for vc in rx.guild.voice_channels:
        if rx.me.permissions_in(vc).connect:
            joinable = True; break
    if not joinable:
        await rx.message.reply(responses.no_permission); return
    for member in rx.guild.members:
        if member.voice:
            while True:
                vc = random.choice(rx.guild.voice_channels)
                if rx.me.permissions_in(vc).connect:
                    break
            await member.move_to(vc)

@bot.command()
async def verify(rx):
    image = random.choice(os.listdir('verify'))
    file = f'verify/{image}'
    await rx.message.reply(file=discord.File(file))

@ri.error
async def ri_error(rx, error):
    if isinstance(error, commands.BadArgument):
        await rx.message.reply(responses.no_channel)

@rm.error
async def rm_error(rx, error):
    if isinstance(error, commands.BadArgument):
        await rx.message.reply(responses.no_user)

@bot.event
async def on_ready():
    print(f'Logged into {bot.user.name}#{bot.user.discriminator} ({bot.user.id})')
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name='you.'))

@bot.event
async def on_command_error(*a):
    pass

queue = threading.Thread(target=dump_queue, daemon=True)
queue.start()
bot.run(token)
