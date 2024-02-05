from discord.ext import commands


class on_ready(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"\033[32m\n 🗿 ► {self.bot.user.name} ha cobrado vida\n\033[39m")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Verificar que el mensaje no sea del propio bot
        if message.author == self.bot.user:
            return

        print(
            f"\033[34m\n 🧑 ► {message.author} ha dicho: {message.content}\n\033[39m")


async def setup(bot):
    await bot.add_cog(on_ready(bot=bot))
