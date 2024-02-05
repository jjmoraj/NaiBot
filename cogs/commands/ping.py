from discord.ext import commands


class ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, message):
        await message.reply("Pong!")


async def setup(bot):
    await bot.add_cog(ping(bot=bot))
