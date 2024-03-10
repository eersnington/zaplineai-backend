from lib.cached_response import VectorDatabase, get_intent_response, get_order_status_response
from lib.llm_model import LLMModel, LLMChat, BERTClassifier
from lib.llm_prompt import llama_prompt
from lib.shopify.resource_base import ShopifyResource
from lib.shopify.shopify_client import ShopifyClient

from lib.db import track_metrics

llm_model = LLMModel()
bert_classifier = BERTClassifier()
vector_db = VectorDatabase()


class CallChatSession:
    def __init__(self, app_token: str, myshopify: str):
        self.sid = None
        self.llm_chat = LLMChat(llm_model, bert_classifier)
        self.app_token = app_token
        self.myshopify = myshopify.split(".")[0]
        self.resource = ShopifyResource(token=app_token, store=myshopify.split(".")[0])
        self.client = ShopifyClient(self.resource)
        self.order_id = None # The ID of the recent order.
        self.vector_db = vector_db
        self.refund_order = False
        self.return_order = False
        self.return_refund_reason = None
    

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
            return "Sorry, we are currently experiencing technical difficulties. Please call again later.", None

        for customer in output.json()["customers"]:                        
            recent_orders = self.client.resource.get(f"/orders.json?customer_id={customer['id']}").json()["orders"]
            
            if len(recent_orders) == 0:
                return " You seem to be new to the store. How can I help you today?", None
            recent_order = recent_orders[0]

            items = recent_order["line_items"]
            item_names = []
            for item in items:
                item_names.append(item["title"])
            date = recent_order["created_at"].split("T")[0]

            self.order_id = recent_order["id"]
            self.order_status = f"{recent_order['fulfillment_status']}"

            response = f" Are you calling regarding your recent purchase of {', '.join(item_names)} on {date}?"
            return response, recent_order["id"]
        
        return " You seem to be new to the store. How can I help you today?", None
    

    def get_order_status(self) -> str:
        """
            Gets the Fulfillment status of recent order.

            Returns:
            str -- The status of the order.
        """
        if self.order_status is None:
            return "none"
        
        return self.order_status


    def initiate_return(self) -> str:
        """
            Initiates a return for the customer.

            Returns:
            str -- The status of the return.
        """
        if self.order_id is None:
            return "I couldn't find any latest orders for you. If you think this is a mistake, please call again later."
        
        print(f"Order ID: {self.order_id}")
        print(type(self.order_id))

        note_text = f"Return initiated by customer through call. Reason: {self.return_refund_reason}"
        
        status = self.client.Orders.update_order(self.order_id, '{"order":{"id":5951600885924,"note":"Customer contacted us about a custom engraving on this iPod"}}')

        print(status.status_code, status.text)
        return get_intent_response("Returns Step2")
    

    def initiate_refund(self) -> str:
        """
            Initiates a refund for the customer.

            Returns:
            str -- The status of the refund.
        """
        if self.order_id is None:
            return "I couldn't find any latest orders for you. If you think this is a mistake, please call again later."

        print(f"Order ID: {self.order_id}")
        print(type(self.order_id))

        note_text = f"Refund initiated by customer through call. Reason: {self.return_refund_reason}"

        status = self.client.Orders.update_order(self.order_id, '{"order":{"id":5951600885924,"note":"Customer contacted us about a custom engraving on this iPod"}}')

        print(status.status_code, status.text)
        return get_intent_response("Refund Step2")
    

    def return_process(self, reason) -> str:
        if self.return_order is False:
            self.return_order = True
            return "true"

        if reason:
            self.return_refund_reason = reason
            self.return_order = False
            response = self.initiate_return()
            return response
            

    def refund_process(self, reason) -> str:
        if self.refund_order is False:
            self.refund_order = True
            return "true"

        if reason:
            self.return_refund_reason = reason
            self.refund_order = False
            return self.initiate_refund()


    def check_call_intent(self, message: str) -> str:
        """
            Checks the intent of the call.

            Keyword arguments:
            message -- The message to be processed.

            Returns:
            str -- The intent of the call.
        """
        self.call_intent = self.llm_chat.get_call_type(message)[0]["label"]
        return self.call_intent
        

    def get_response(self, message: str) -> str:
        """
            Check the call intent, search the cache for a response and return if found, else call the LLM model.

            Keyword arguments:
            message -- The message to be processed by the LLM model.

            Returns:
            str -- The response from the LLM model.
        """

        if self.refund_order is True:
            return self.refund_process(message)
        
        if self.return_order is True:
            return self.return_process(message)

        cached_response = self.vector_db.find_similar_response(message)

        if cached_response is not None:
            if cached_response.endswith("<<explain the current status of your order>>"):
                self.call_intent = "Order Status"
                data = self.get_order_status()
                print("Order Status: ", data)
                addon = get_order_status_response(data)
                if addon is None:
                    addon = "I couldn't find any recent orders "
                cached_response = cached_response.replace("<<explain the current status of your order>>", addon)

            elif "return" in cached_response or "returning" in cached_response:
                self.call_intent = "Returns"
                self.return_process(None) # This is a dummy call to set the return_order flag to True (Returns Step 1)

            elif "refund" in cached_response or "refunding" in cached_response:
                self.call_intent = "Refund"
                self.refund_process(None) # This is a dummy call to set the refund_order flag to True (Refund Step 1)

            print(f"Call Intent: {self.call_intent}")
            return cached_response
        
        call_intent = self.check_call_intent(message)
        print(f"Call Intent: {call_intent}")


        if call_intent == "Returns":
            pass

        
        if call_intent == "General Inquiry":
            data = ""
        elif call_intent == "Product Info":
            data = "Provide the customer with the information they are looking for."
        elif call_intent == "Sales":
            data = "Transferring to sales team. Please wait."
        else:
            data = ""

        prompt = llama_prompt(message, call_intent, data, self.llm_chat.chat_history)       
        
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

    def get_call_intent(self) -> str:
        """
            Gets the classified call intent

            Keyword arguments:
            message -- The message to be processed.

            Returns:
            str -- The intent of the call.
        """
        return self.call_intent
        
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
        elif call_intent == "Transfer":
            call_type = "transfer"
        
        return call_type
    

    