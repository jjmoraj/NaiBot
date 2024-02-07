from dotenv import load_dotenv
import os
from langfuse.callback import CallbackHandler
from langchain_openai import ChatOpenAI


load_dotenv()


class NaiModel():
    def __init__(self, temperature=0, streaming=False):
        self.together_token = os.getenv('TOGETHER_TOKEN')
        self.langfuse_sk = os.getenv('LANGFUSE_SECRET_KEY')
        self.langfuse_pk = os.getenv('LANGFUSE_PUBLIC_KEY')
        self.model_name = 'mistralai/Mixtral-8x7B-Instruct-v0.1'
        self.base_url = 'https://api.together.xyz'
        self.temperature = temperature
        self.streaming = streaming
        self.langfuse_callbak = CallbackHandler(
            self.langfuse_pk, self.langfuse_sk)

    def get_model(self):

        model = ChatOpenAI(
            base_url=self.base_url,
            model=self.model_name,
            api_key=self.together_token,
            streaming=self.streaming,
            temperature=self.temperature,
            callbacks=[self.langfuse_callbak]
        )

        return model
