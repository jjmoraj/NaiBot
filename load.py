import os

#! Carga los comandos / cogs del bot


async def load(bot):
    for filename in os.listdir('./src/cogs/commands'):
        if filename.endswith('.py'):
            cog_name = f'src.cogs.commands.{filename[:-3]}'
            await bot.load_extension(cog_name)

    for filename in os.listdir('./src/cogs/events'):
        if filename.endswith('.py'):
            cog_event = f'src.cogs.events.{filename[:-3]}'
            await bot.load_extension(cog_event)
