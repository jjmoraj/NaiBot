from src.cogs.cogs_dict import get_cogs_dict


class NaiCommandsAgent():
    def __ini__(self):
        self.name = 'CommandFilter'
        self.cogs_dict = str(get_cogs_dict())
        self.description = f'''
        
            Tool to identify the type of command the user wants to make by natural language.
            Returns a specific command according to the commands that will be provided.
            You will receive a message from the user, which you will have to identify what kind of command he/she wants to do.
            For this you will be given a json with the list of available commands, and the description of these, so that from the description of each command you can return its name.

            List of commands:

            {self.cogs_dict}


            Analyze step by step this dictionary of values, and return the value, which you think is correct, according to the description of the command.

            You will have to answer a message that is a dictionary, with the key command, and the value that you think is correct.

            Example 1:
                User asks: "I want a pong".
                You should answer the following {'command':'ping'}

            Example 2:
                User asks: "I want to know how the bot works".
                You should answer the following {'command':'helpCommand'} 
        '''
