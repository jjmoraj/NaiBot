import discord
from discord import Embed
from discord.ext import commands

""" //- COMMANDS -// """


class support(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=['hc'],
        description='A continuación se muestran todos los comandos del bot',
        help='Embed informativo para utilizar los comandos del bot',
        brief='Embed informativo para utilizar los comandos del bot'
    )
    #! Embed informativo para utilizar los comandos del bot
    async def helpCommand(self, message):
        usuario = message.author.mention
        embed = discord.Embed(
            title="Comandos de NAI",
            description=f"A continuación, {usuario} se muestran todos los comandos del bot",
            color=discord.Color.green()
        )

        embed.set_thumbnail(
            url="https://icones.pro/wp-content/uploads/2021/05/icone-d-information-vert.png")

        # Ordenar en orden alfabético

        embed.add_field(
            name="`!hc / !helpCommand`", value="NAI nos dará una guía de sus comandos para que los usemos", inline=False)

        embed.add_field(
            name="`!cogs / !listcogs`", value="NAI muestra la lista de cogs cargados con sus respectivos comandos", inline=False)

        embed.add_field(
            name="`!p / !ping`", value="NAI contesta con un 'Pong!'", inline=False)

        embed.set_footer(text="Espero que te haya ayudado")

        await message.send(embed=embed)

    @commands.command(
        aliases=['cogs'],
        description='Un comando para ver los COGS cargados de NAI',
        help='Un comando para ver los COGS cargados de NAI',
        brief='Un comando para ver los COGS cargados de NAI'
    )
    async def listcogs(self, message):
        """Lists all loaded cogs and their commands"""
        embed = Embed(
            title="Cogs cargados",
            description="Estos son los cogs actualmente cargados y sus comandos:",
            color=0x42f56c
        )
        for cog_name, cog in self.bot.cogs.items():
            commands = [f'`{command.name}`' for command in cog.get_commands()]
            commands_str = ', '.join(
                commands) if commands else 'No hay comandos en este cog.'
            embed.add_field(name=cog_name, value=commands_str, inline=False)
        await message.reply(embed=embed)


""" //- SETUP -// """


async def setup(bot):
    await bot.add_cog(support(bot=bot))
