from lib.llm_model import LLMModel, LLMChat, BERTClassifier
from lib.shopify.resource_base import ShopifyResource
from lib.shopify.shopify_client import ShopifyClient

llm_model = LLMModel()
bert_classifier = BERTClassifier()


class CallChatSession:
    def __init__(self, app_token:str, myshopify:str):
        self.sid = None
        self.llm_chat = LLMChat(llm_model)
        self.resource = ShopifyResource(token=app_token, store=myshopify)
        self.client = ShopifyClient(self.resource)

    def start(self, sid:str) -> None:
        """
            Handles the audio stream of a call session.

            Keyword arguments:
            websocket -- The websocket instance used to receive the audio stream from Twilio.
        """
        self.sid = sid

    def get_response(self, message:str) -> str:
        """
            Gets response from the LLM model.

            Keyword arguments:
            message -- The message to be processed by the LLM model.

            Returns:
            str -- The response from the LLM model.
        """
        return self.llm_chat.get_response(message)
    
    def get_shopify_status(self) -> int:
        """
            Gets the status of the Shopify API.

            Returns:
            int -- The status code of the Shopify API.
        """
        return self.client.status()

    

    