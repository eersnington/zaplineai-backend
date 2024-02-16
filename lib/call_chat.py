from lib.llm_model import LLMModel, LLMChat, BERTClassifier
from lib.llm_prompt import llama_prompt
from lib.shopify.resource_base import ShopifyResource
from lib.shopify.shopify_client import ShopifyClient

from lib.db import track_metrics

llm_model = LLMModel()
bert_classifier = BERTClassifier()


class CallChatSession:
    def __init__(self, app_token: str, myshopify: str):
        self.sid = None
        self.llm_chat = LLMChat(llm_model, bert_classifier)
        self.resource = ShopifyResource(token=app_token, store=myshopify.split(".")[0])
        self.client = ShopifyClient(self.resource)
        self.order_id = None # The ID of the recent order.
    

    def start(self, sid: str, customer_phone_no: str) -> str:
        """
            Handles first interaction with the call session.

            Keyword arguments:
            sid -- The call session ID.
            customer_phone_no -- The phone number of the customer.
        """
        self.sid = sid
        output = self.client.resource.get(f"/customers.json?phone={customer_phone_no}")

        if output.status_code != 200:
            return "Sorry, we are currently experiencing technical difficulties. Please call again later."

        for customer in output.json()["customers"]:                        
            recent_orders = self.client.resource.get(f"/orders.json?customer_id={customer['id']}").json()["orders"]
            
            if len(recent_orders) == 0:
                return " You seem to be new to the store. How can I help you today?"
            recent_order = recent_orders[0]

            items = recent_order["line_items"]
            item_names = []
            for item in items:
                item_names.append(item["title"])
            date = recent_order["created_at"].split("T")[0]

            self.order_id = recent_order["id"]
            self.order_status = f"Financial Status of Order: {recent_order['financial_status']}. Fulfillment status of Order: {recent_order['fulfillment_status']}"

            response = f" Are you calling regarding your recent purchase of {', '.join(item_names)} on {date}?"
            return response
        
        return " You seem to be new to the store. How can I help you today?"
    
    def get_order_status(self) -> str:
        """
            Gets the status of recent order.

            Returns:
            str -- The status of the order.
        """
        if self.order_status is None:
            return "I couldn't find any latest orders for you. Please call again later."
        
        return self.order_status
        
    def initiate_refund(self) -> str:
        """
            Initiates a refund for the customer.

            Returns:
            str -- The status of the refund.
        """
        if self.order_id is None:
            return "I couldn't find any latest orders for you. Please call again later."
        
        self.client.Orders.update_order(self.order_id, {"order": {"note": "Refund initiated by customer through call."}})
        return "Server: Refund initiated successfully."
        
    def initiate_return(self) -> str:
        """
            Initiates a return for the customer.

            Returns:
            str -- The status of the return.
        """
        if self.order_id is None:
            return "I couldn't find any latest orders for you. Please call again later."
        
        self.client.Orders.update_order(self.order_id, {"order": {"note": "Return initiated by customer through call."}})
        return "Server: Return initiated successfully."
        
    def get_response(self, message: str) -> str:
        """
            Gets response from the LLM model.

            Keyword arguments:
            message -- The message to be processed by the LLM model.

            Returns:
            str -- The response from the LLM model.
        """

        call_type = self.llm_chat.get_call_type(message)

        if call_type[0]["label"] == "Order Status":
            data =  self.get_order_status()
        else:
            data = ""

        prompt = llama_prompt(message, call_type, data, self.llm_chat.chat_history)       
        
        return self.llm_chat.generate_response(message, prompt)
    
    def get_shopify_status(self) -> int:
        """
            Gets the status of the Shopify API.

            Returns:
            int -- The status code of the Shopify API.
        """
        return self.client.status()
    
    def update_call_status(self, user_id: str, call_type: str, call_intent: str) -> str:
        """
            Updates the status of the call.

            Keyword arguments:
            user_id -- The user's ID.
            call_type -- The type of call to be tracked.
            call_intent -- The intent of the call.
        """
        try:
            track_metrics(user_id, call_type)
        except Exception as e:
            return f"Error occurred: {str(e)}"
        return "Call status updated successfully."

    def get_call_intent(self, message: str) -> str:
        """
            Gets the intent of the call.

            Keyword arguments:
            message -- The message to be processed.

            Returns:
            str -- The intent of the call.
        """
        return self.llm_chat.get_call_type(message)[0]["label"]
    
    def get_call_type(self, call_intent: str) -> str:
        """
            Gets the type of the call.

            Keyword arguments:
            call_intent -- The intent of the call.

            Returns:
            str -- The type of the call.
        """
        call_type = "automated"
        if call_intent == "Sales":
            call_type = "transfer"
        elif call_type == "Transfer":
            call_type = "transfer"
        
        return call_type
    

    