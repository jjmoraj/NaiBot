import discord
from discord.ext import commands

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandNotFound):
            await ctx.send('¡Comando no encontrado!')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Falta un argumento requerido.')
        else:
            await ctx.send('Ocurrió un error.')
            print(f'Error: {error}')


async def setup(bot):
    await bot.add_cog(ErrorHandler(bot=bot))