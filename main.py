import os
import asyncio
import discord
from discord.ext import commands

#! Para cargar los comandos del bot
from src.cogs.cogs_dict import get_cogs_dict
from load import load

from dotenv import load_dotenv
load_dotenv()


async def main(bot, token):
    await load(bot=bot)

    #! Lista de cogs para la comprobación por lenguaje natural
    cogs_dict = await get_cogs_dict(bot=bot)
    print(cogs_dict)

    await bot.start(token=token)


class NAI(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        intents.members = True
        token = os.getenv('BOT_TOKEN')

        super().__init__(
            command_prefix='!',
            intents=intents,
            description="Soy NAI, tu asistente inteligente")

        asyncio.run(main(bot=self, token=token))


if __name__ == '__main__':
    botNia = NAI()
