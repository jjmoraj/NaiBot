import os


async def load(bot):
    for filename in os.listdir('./cogs/commands'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

    for filename in os.listdir('./cogs/events'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
