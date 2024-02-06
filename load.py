import os

#! Carga los comandos / cogs del bot


async def load(bot):
    for filename in os.listdir('./src/cogs/commands'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.commands.{filename[:-3]}')

    for filename in os.listdir('./src/cogs/events'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.events.{filename[:-3]}')
