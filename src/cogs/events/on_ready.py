from discord.ext import commands

""" //- EVENTS -// """


class on_ready(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.command_agent

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"\033[32m\n 🗿 ► {self.bot.user.name} ha cobrado vida\n\033[39m")
        
        music_channel = 'nai_music'
        
        for guild in self.bot.guilds:
            # Obtén el ID del servidor (guild)
            guild_id = guild.id
            
        # Obtiene la lista de canales de texto en el servidor
        text_channel_list = [channel.name for channel in guild.text_channels]
        
        print(f"Los canales de texto en el servidor con ID {guild_id} son: {', '.join(text_channel_list)}")
            
        # Si el canal de música no está en la lista, puedes crearlo
        if music_channel not in text_channel_list:
            await guild.create_text_channel(music_channel)


    @commands.Cog.listener()
    async def on_message(self, message):

        # Verificar que el mensaje no sea del propio bot
        if message.author == self.bot.user:
            return

        print(
            f"\033[34m\n 🧑 ► {message.author} ha dicho: {message.content}\n\033[39m"
        )

""" //- SETUP -// """


async def setup(bot):
    await bot.add_cog(on_ready(bot=bot))
