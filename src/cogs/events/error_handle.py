from discord.ext import commands
from src.cogs.cogs_dict import get_cogs_dict
from src.llm.classification_agent import NaiClassificationAgent
from src.llm.model import NaiModel
import json

from  src.cogs.commands.basics import basics

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        cogs_dict = await get_cogs_dict(bot=self.bot)

        if isinstance(error, commands.errors.CommandNotFound):

            message = ctx.message

            if message.author == self.bot.user:
                return

            nai_model = NaiModel()

            classification_agent = NaiClassificationAgent(cogs_dict=cogs_dict)
            
            clasificated_message = await classification_agent.get_classicated_message(message=message,model=nai_model)

           
            message.content = f"!{clasificated_message['response_type']}"


            await self.bot.process_commands(message)


        elif isinstance(error, commands.MissingRequiredArgument):
            await message.send('Falta un argumento requerido.')
        else:
            await message.send('Ocurrió un error.')
            print(f'Error: {error}')


async def setup(bot):
    await bot.add_cog(ErrorHandler(bot=bot))
