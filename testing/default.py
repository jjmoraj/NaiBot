import os
import discord

from dotenv import load_dotenv
load_dotenv()


class NAI(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')


intents = discord.Intents.all()
intents.message_content = True
intents.members = True

client = NAI(intents=intents)
client.run(os.getenv('BOT_TOKEN'))
