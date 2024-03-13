from discord.ext import commands
from src.cogs.cogs_dict import get_cogs_dict
from src.llm.classification_agent import NaiClassificationAgent
from src.llm.model import NaiModel
import json
import discord

from src.llm.tools.nai_assistant.normal_response_tool import NaiAssitantAgent

from src.cogs.commands.basics import basics


class errorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        cogs_dict = await get_cogs_dict(bot=self.bot)

        if isinstance(error, commands.errors.CommandNotFound):

            message = ctx.message

            if message.author == self.bot.user:
                return


            if message.channel.name == 'nai-assistant':

                nai_model = NaiModel()

                nai_assistant = NaiAssitantAgent()

                response = await nai_assistant.assistant_response(message=message,model=nai_model)

                is_nitro = any(guild.premium_tier > 1 for guild in self.bot.guilds)

                if len(response) >= 2000 and not is_nitro:
                    embed = discord.Embed(title='Nai Assistant',description=response)

                    await message.reply(embed=embed)
                else:
                    await message.reply(response)

            else:
                nai_model = NaiModel()

                classification_agent = NaiClassificationAgent(cogs_dict=cogs_dict)
                
                clasificated_message = await classification_agent.get_classicated_message(message=message,model=nai_model)

            
                message.content = f"!{clasificated_message['response_type']}"


        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Falta un argumento requerido.')
        else:
            await ctx.send('Ocurrió un error.')
            print(f'Error: {error}')


async def setup(bot):
    await bot.add_cog(errorHandler(bot=bot))
