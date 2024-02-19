from langchain_core.messages import SystemMessage, HumanMessage
import json


class NaiClassificationAgent():
    def __init__(self, cogs_dict):
        self.name = 'ClassifyUserMessage'
        self.cogs_dict = cogs_dict
        self.normal_functions = {
            "normal_response": "Reply with 'normal_response' if the user wants a generic response that does not require an internet search and is not current",
            "internet_response": "Reply with 'internet_response', if the user wants a response that requires an internet search and that requires current and updated data",
            "bot_information": "Reply with 'bot_information', if the user wants information about this bot, such as who are its creators, what is its website, etc. "
        }

        self.bot_functions = {
            **self.cogs_dict,
            **self.normal_functions
        }

        self.description = f"""

            Your function right now is to classify the type of response the user should receive.

            The types of messages you can give are the following, they will be passed to you in dictionary format, where the dictionary key is the name of the type of response and the value is its description:

            Here I leave you with the functions that this bot can perform:

            {str(self.bot_functions)}

            Your response must be in dictionary format, with the key 'response_type', where the value is the key of the type of response.

            Here are some examples:

            Example 1:
            Prompt user: I want to know how much is gta 5 worth.
            Response : "{str({"response_type":"internet_response"})}"

            Example 2:
            Prompt user: I want to know the functions of this bot
            Response : {str({"response_type":"helpCommand"})}

            Example 3:
            User Prompt: Tell me pong
            Response : {str({"response_type":"ping"})}

            REMEMBER TO RESPOND ONLY IN DICTIONARY FORMAT AND ONLY WITH THE KEY THAT IS INDICATED AND THE VALUE OF THE TYPE OF RESPONSE THAT THE USER WANTS, IT IS VERY IMPORTANT THAT YOU DO NOT RESPOND WITH ANYTHING ELSE, NO MORE INFORMATION.

            If you are not clear, the type of response the user wants or the command is not defined, respond with "{str({"response_type":"normal_response"})}".

            Remember that dictionary values, both the key and the value are enclosed in double quotes "".
            Remember to take a deep breath, and go through everything step by step, before answering, answering only with the indicated format.
            
            Here is the user's prompt:

            """

    async def get_classicated_message(self, message, model):

        prompt_messages = [
            SystemMessage(content=self.description),
            HumanMessage(content=str(message.content[1:])),
        ]
        llm = model.get_model()
        llm_response = llm.invoke(prompt_messages)
        llm_response = {
            'response_type': 'normal_response'} if None else llm_response

        llm_response = str(llm_response.content).replace(
            "\\", "").replace('\'', '"')
        llm_response = json.loads(llm_response)

        llm_response['response_type'] = llm_response['response_type'] if llm_response['response_type'] in list(
            self.bot_functions.keys()) else 'normal_response'

        return llm_response
