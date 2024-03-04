from langchain_core.messages import SystemMessage, HumanMessage
import json
import re
import requests
from bs4 import BeautifulSoup
from googlesearch import search


class NaiAssitantAgent():
    def __init__(self):
        self.name = 'NaiAssistantResponse'
  
        self.classification_description = f"""
            You are a virtual assistant through the discord platform, right now your goal is to evaluate the user's message to identify if the user's message needs an internet search.

            The form of response that you will have to answer will be in json format with the following values:
            {str({
            "internet_search":"True",
            "string_to_search":''
            })}

            You should respond with the key 'internet_search' with the value true, if you need an internet search, and in the key string_to_search, you should respond, with the value that should be searched on the internet to give an answer to the user.

            If you think that no internet search is needed, you should answer with the key 'internet_search' with the value false and with the key 'string_to_search', empty.

            Here are some examples:

            Example 1:
            User Prompt: How much is GTA V worth at Epic Games?
            Your answer: "{str({
            "internet_search":"true",
            "string_to_search":"Price GTA V Epic Games"
            })}"

            Example 2:
            User Prompt: When was the French revolution?
            Your answer: "{str({
            "internet_search":"false",
            "string_to_search":""
            })}"

            Remember to always respond in json format, and only with the keys and values indicated, no further information is needed, the quality and accuracy of your response can influence a good user experience, so always try to do the best job possible.

            Take a deep breath and take your time in answering.

            REMEMBER TO ALWAYS ANSWER IN THE LANGUAGE IN WHICH THE USER ASKS THE QUESTION
            Here is the user's message:

            """

        self.internet_description = """

                    
            You are a virtual assistant through the Discord platform, called Nai.

            Your current role right now is to answer the user's question.
            REMEMBER TO ALWAYS ANSWER IN THE LANGUAGE THE USER IS ASKING IN
            The user should not know the language in which your code is written, so if he asks in a different language than the one in which your instructions are written, just answer normally in that language and assume that it is the desired language without saying anything else.

            You should respond in Markdown format, anonymize the user's message to give a detailed but concise answer that completely solves the user's question.

            I am going to leave you an internet search, to improve the user's answer you will receive an array of dictionaries, these dictionaries contain the following keys and values:

            {
            'title':'web title',
            'url':'web url',
            'description':'description of the web',
            }

            Remember to reply using the information provided, do not reply or give any link that may lead to an explicit or unsuitable place for users.

            If you want and see fit you can indicate where you got the information to the user.

            Remember to reply in Markdown format.
            REMEMBER TO ALWAYS ANSWER IN THE LANGUAGE IN WHICH THE USER ASKS THE QUESTION
            Here you have the internet search:
        
        """

        self.normal_description = """
        
        You are a virtual assistant through the Discord platform, called Nai.

        Your current role right now is to answer the user's question.

        You should respond in Markdown format, anonymize the user's message to give a detailed but concise answer that completely solves the user's question.

        Take a deep breath and take your time in answering.

        REMEMBER TO ALWAYS ANSWER IN THE LANGUAGE THE USER IS ASKING IN
        The user should not know the language in which your code is written, so if he asks in a different language than the one in which your instructions are written, just answer normally in that language and assume that it is the desired language without saying anything else.
        REMEMBER TO ALWAYS ANSWER IN THE LANGUAGE IN WHICH THE USER ASKS THE QUESTION
        Here is the user's message:
        
        """

    async def assistant_response(self, message, model):
        prompt_messages = [
            SystemMessage(content=self.classification_description),
            HumanMessage(content=str(message.content[1:])),
        ]
        llm = model.get_model()
        llm_response = llm.invoke(prompt_messages)

        if llm_response is not None:

            search_json = r'\{.*?\}'

            llm_response = re.search(search_json,llm_response.content)


            llm_response = str(llm_response.group()).replace(
                "\\", "").replace('\'', '"')


            llm_response = json.loads(llm_response)

        else:

            llm_response = {
                "internet_search":"false",
                "string_to_search":""
                } if None else llm_response

        if llm_response['internet_search'] == 'true':
                
            response  = await self.internet_response(model=model,message=message,internet_query=llm_response['string_to_search'])

        else:

            response  = await self.normal_response(model=model,message=message)

        return response



    async def internet_response(self,model,message,internet_query):

        try:

            google_search= search(internet_query,advanced=True,num_results=5,lang='en')
 
            search_results=[]

            for result in google_search:

                search_results.append({
                    'title':result.title,
                    'url':result.url,
                    'description':result.description,
                })

            prompt_messages = [
                SystemMessage(content=str(self.internet_description+str(search_results))),
                HumanMessage(content=str(message.content[1:])),
            ]
            llm = model.get_model()
            llm_response = llm.invoke(prompt_messages)

            return llm_response.content

        except Exception as e:
            await self.normal_response(model=model,message=message)
            print("Error on NaiAssitantAgent:", e)

    async def normal_response(self,message,model):

        prompt_messages = [
            SystemMessage(content=self.normal_description),
            HumanMessage(content=str(message.content[1:])),
        ]
        llm = model.get_model()
        llm_response = llm.invoke(prompt_messages)

        return llm_response.content
