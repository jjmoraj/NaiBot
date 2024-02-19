import os

#! Carga los comandos / cogs del bot


async def load(bot):
    #! Cogs and commands
    for filename in os.listdir('./src/cogs/commands'):
        if filename.endswith('.py'):
            cog_name = f'src.cogs.commands.{filename[:-3]}'
            await bot.load_extension(cog_name)

    #! Events
    for filename in os.listdir('./src/cogs/events'):
        if filename.endswith('.py'):
            cog_event = f'src.cogs.events.{filename[:-3]}'
            await bot.load_extension(cog_event)

    #! Music Bot
    for filename in os.listdir('./src/cogs/music_bot'):
        if filename.endswith('.py'):
            cog_event = f'src.cogs.music_bot.{filename[:-3]}'
            await bot.load_extension(cog_event)
