from discord.ext import commands
from src.cogs.cogs_dict import get_cogs_dict
from src.llm.classification_agent import NaiClassificationAgent
from src.llm.model import NaiModel
from langchain_core.messages import SystemMessage, HumanMessage
import json

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        
        cogs_dict = await get_cogs_dict(bot=self.bot)

        if isinstance(error, commands.errors.CommandNotFound):

            message = ctx.message
            nai_model =  NaiModel()
            classification_agent = NaiClassificationAgent(cogs_dict=cogs_dict)
            prompt_messages = [
                SystemMessage(content=classification_agent.description),
                HumanMessage(content= str(message.content[1:])),
            ]
            llm = nai_model.get_model()
            llm_response = llm.invoke(prompt_messages)
            llm_response = {'response_type':'normal_response'} if None else llm_response  

            llm_response = str(llm_response.content).replace("\\", "").replace('\'', '"')
            llm_response = json.loads(llm_response)

            llm_response['response_type'] = llm_response['response_type'] if  llm_response['response_type']  in list(classification_agent.bot_functions.keys()) else 'normal_response'

            await message.reply(llm_response['response_type'])

            
        elif isinstance(error, commands.MissingRequiredArgument):
            await message.send('Falta un argumento requerido.')
        else:
            await message.send('Ocurrió un error.')
            print(f'Error: {error}')


async def setup(bot):
    await bot.add_cog(ErrorHandler(bot=bot))