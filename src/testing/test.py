import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


class NIA(commands.Bot):
    def __init__(self, intents):
        super().__init__(command_prefix='*', intents=intents,
                         description="Soy Nai, tu asistente inteligente")

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')


class Tool():
    def __init__(self, bot, name, description):
        self.bot = bot
        self.name = name
        self.description = description


class WelcomeTool(Tool):
    def __inti__(self, bot, name, description, message):
        super().__init__(bot, name, description)
        self.message = message

    async def welcome_greetings(self):
        await self.bot.send(self.message, username=self.bot.username)


if __name__ == '__main__':
    intents = discord.Intents.all()
    token = os.getenv('BOT_TOKEN')

    nia_bot = NIA(intents)

    welcome_tool = WelcomeTool(
        nia_bot, 'prueba', 'esto es una prueba')

    welcome_tool.welcome_greetings()

    #! Es lo último
    nia_bot.run(token)
