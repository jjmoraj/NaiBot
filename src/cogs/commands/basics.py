from discord.ext import commands

""" //- COMMANDS -// """


class basics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=['p'],
        description="Responde al usuario con un 'Pong', si el usario dice 'Ping'",
        help="NAI responde al usuario con un 'Pong!'",
        brief="NAI responde al usuario con un 'Pong!'"
    )
    async def ping(self, message):
        await message.reply("Pong!")

    @commands.command(
        aliases=['h'],
        description="Saluda al usuario si este lo saluda a el",
        help="NAI saluda al usuario",
        brief="NAI saluda al usuario"
    )
    async def hello(self, message):
        await message.reply(f"¡Hola {message.author.mention}!")


""" //- SETUP -// """


async def setup(bot):
    await bot.add_cog(basics(bot=bot))
