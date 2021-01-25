class Message:
    def __init__(self, body, author, timestamp, attachments=None):
        self.body = body
        self.author = author
        self.timestamp = timestamp
        self.attachments = attachments

class QueuedFile:
    def __init__(self, url, channel, id):
        self.url = url
        self.channel = channel
        self.id = id

class Responses:
    def __init__(self):
        self.guild_not_dumped= 'Awoo... I couldn\'t find any dumped channels.'
        self.channel_not_dumped = 'Awoo... this channel is not dumped.'
        self.channel_dumping = 'Awoo... this channel is currently dumping, please wait.'
        self.user_not_dumped = 'Awoo... this user has not been researched.'
        self.no_permission = 'Awoo... you don\'t have permission.'
        self.no_channel = 'Awoo... channel not found.'
        self.no_user = 'Awoo... user not found.'
        self.no_voice_channel = 'Awoo... you are not in a voice channel.'
