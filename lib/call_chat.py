from lib.cached_response import VectorDatabase, get_intent_response, get_order_status_response
from lib.llm_model import LLMModel, LLMChat, BERTClassifier
from lib.llm_prompt import llama_prompt, get_classifier_prompt
import shopify

from lib.db import track_metrics


llm_model = LLMModel()
bert_classifier = BERTClassifier()
vector_db = VectorDatabase()


class CallChatSession:
    def __init__(self, app_token: str, myshopify: str):
        self.sid = None
        self.llm_chat = LLMChat(llm_model, bert_classifier)
        self.app_token = app_token
        self.myshopify = myshopify
        self.client = shopify.Session(myshopify, "2024-01", app_token)
        shopify.ShopifyResource.activate_session(self.client)
        self.order_id = None # The ID of the recent order.
        self.vector_db = vector_db
        self.refund_order = False
        self.return_order = False
        self.cancel_order = False
        self.return_refund_reason = None
        self.call_intent = None
        self.order = None
        self.order_status = None
    

    def start(self, sid: str, customer_phone_no: str) -> str:
        """
        Handles first interaction with the call session.

        Args:
        - sid (str): The call session ID.
        - customer_phone_no (str): The phone number of the customer.

        Returns:
            str: The response to the customer's call initiation.
        """

        print("My Shopify Link:", self.myshopify)
        try:
            self.sid = sid
            orders = shopify.Order.find()
            recent_order = None

            for order in orders:
                if order.customer and order.customer.phone == customer_phone_no:
                    recent_order = order
                    break

            if recent_order is None:
                return " You seem to be a new customer based on my records. How can I help you today?"
            
            self.order = recent_order

            print("Recent Order: ", recent_order.id, recent_order.order_number, recent_order.customer.phone,)

            items = recent_order.line_items
            item_names = [item.title for item in items]
            date = recent_order.created_at.split("T")[0]

            self.order_id = recent_order.id
            self.order_status = recent_order.fulfillment_status
            self.order = recent_order

            response = f" You've a recent order of {', '.join(item_names)}. Do you wanna know the order status, start a return, or anything else?"
            return response
        except Exception as e:
            return "Exception"
    

    def get_order_status(self) -> str:
        """
        Gets the Fulfillment status of recent order.

        Returns:
            str: The status of the order.
        """
        if self.order is None:
            return "none"
        else:
            if self.order_status is None:
                self.order_status = "unfulfilled"
        
        return self.order_status
    

    def initiate_cancel(self) -> str:
        """
        Cancels the order of the customer through Shopify.

        Returns:
        str -- The response message of the bot indicating the status of the cancel.
        """
        if self.order is None:
            return "I couldn't find any latest orders for this number. If you think this is a mistake, I can transfer the call for you."

        note_text = f"Cancel initiated by customer through call. Reason: {self.return_refund_reason}"
        print("Order ID:", self.order.id)

        try:
            self.order.note = note_text
            self.order.save()
        except Exception as e:
            print(e)

        return get_intent_response("Cancel Step2")


    def initiate_return(self) -> str:
        """
        Returns the order of the customer through Shopify.

        Returns:
        str -- The response message of the bot indicating the status of the return.
        """
        if self.order is None:
            return "I couldn't find any latest order for this number. If you think this is a mistake, I can transfer the call for you."
        
        note_text = f"Return initiated by customer through call. Reason: {self.return_refund_reason}"
        print("Order ID:", self.order.id)
        
        try: # can crash if the correct myshopify link is not provided
            self.order.note = note_text
            self.order.save()
        except Exception as e:
            print(e)
        
        return get_intent_response("Returns Step2")
    

    def initiate_refund(self) -> str:
        """
        Refunds the order of the customer through Shopify.

        Returns:
        str -- The response message of the bot indicating the status of the refund.
        """
        if self.order is None:
            return "I couldn't find any latest orders for this number. If you think this is a mistake, I can transfer the call for you."

        note_text = f"Refund initiated by customer through call. Reason: {self.return_refund_reason}"
        print("Order ID:", self.order.id)

        try:
            self.order.note = note_text
            self.order.save()
        except Exception as e:
            print(e)

        return get_intent_response("Refund Step2")
    

    def cancel_process(self, reason) -> str:
        if self.cancel_order is False:
            self.cancel_order = True
            return "true"

        if reason:
            self.return_refund_reason = reason
            self.cancel_order = False
            response = self.initiate_cancel()
            return response

    
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


    def classify_call_intent(self, message: str) -> str:
        """
        Classifies the intent of the message using the BERT Classifier.

        Args:
        - message (str): The message to be classified.

        Returns:
            str. The intent of the call.
        """
        self.call_intent = self.llm_chat.get_call_type(message)[0]["label"]
        return self.call_intent
        

    def get_response(self, message: str) -> str:
        """
        Response workflow of the bot for various intents.

        1. Check if in a refund, return, or cancel process, and handle message accordingly.
        2. Check cached responses. If found, process it.
        3. If no cached response, classify call intent, get relevant data, and generate a response using LLM model.

        Args:
        - message (str): The message to be processed by the LLM model.

        Returns:
            str: The response from the LLM model.
        """

        if self.refund_order is True:
            return self.refund_process(message)
        
        if self.return_order is True:
            return self.return_process(message)
        
        if self.cancel_order is True:
            return self.cancel_process(message)
        
        self.llm_chat.add_message(f"Customer: {message}")

        cached_response = self.vector_db.find_similar_response(message)

        if cached_response is not None:
            if "<<explain the current status of your order>>" in cached_response:
                self.call_intent = "Order Status"
                data = self.get_order_status()
                print("Order Status: ", data)
                addon = get_order_status_response(data)
                if addon is None:
                    addon = "I couldn't find any recent orders for this phone number. If you think this is a mistake, I can transfer the call for you."
                cached_response = cached_response.replace("<<explain the current status of your order>>", addon)

            elif "cancellation" in cached_response:
                self.call_intent = "Cancellation"
                self.cancel_process(None) # This is a dummy call to set the cancel_order flag to True (Cancel Step 1)

            elif "return" in cached_response or "returning" in cached_response:
                self.call_intent = "Returns"
                self.return_process(None) # This is a dummy call to set the return_order flag to True (Returns Step 1)

            elif "refund" in cached_response or "refunding" in cached_response:
                self.call_intent = "Refund"
                self.refund_process(None) # This is a dummy call to set the refund_order flag to True (Refund Step 1)

            elif "sales representative" in cached_response:
                self.call_intent = "Sales"
            
            elif "live representative" in cached_response:
                self.call_intent = "Transfer"

            print(f"Call Intent: {self.call_intent}")

            self.llm_chat.add_message(f"AI Assistant: {cached_response}")
            return cached_response
        
        call_intent = self.classify_call_intent(message)
        self.call_intent = call_intent
        print(f"Call Intent: {call_intent}")

        data = None
        if call_intent == "Order Status":
            status = self.get_order_status()
            data = get_order_status_response(status)
            if data is None:
                data = "I couldn't find any recent orders for this phone number. If you think this is a mistake, please try calling me again."
        elif call_intent == "Returns":
            self.return_process(None)
        elif call_intent == "Refund":
            self.refund_process(None)

        prompt = llama_prompt(message, call_intent, data, self.llm_chat.chat_history)       
        response = self.llm_chat.generate_response(message, prompt)

        # self.vector_db.add_response(message, response) # WORK IN PROGRESS
        self.llm_chat.add_message(f"AI Assistant: {response}")
        return response
    
    def get_shopify_status(self) -> int:
        """
        Gets the status of the Shopify API.

        Returns:
            Bool. The status of the Shopify API.
        """
        try:
            shop = shopify.Shop.current()
            # If we reach this point, the connection was successful
            return True
        except Exception as e:
            # If any exception occurs, the connection failed
            print(f"Failed to connect to Shopify: {e}")
            return False

    def get_call_intent(self) -> str:
        """
        Gets the classified call intent of the call.

        Returns:
            str. The intent of the call.
        """
        return self.call_intent
        
    def get_call_type(self, call_intent: str) -> str:
        """
        Gets the type of the call based on the intent provided.

        Args:
        - call_intent (str): The intent of the call.

        Returns:
            str. The type of the call.
        """
        call_type = "automated"
        if call_intent == "Sales":
            call_type = "transferred"
        elif call_intent == "Transfer":
            call_type = "transferred"
        return call_type
    

    def track_call(self, user_id: str, call_intent: str) -> str:
        """
        Tracks the call metrics for the user.

        Args:
        - user_id (str): The user's ID.
        - call_intent (str): The intent of the call.

        Returns:
            str: The status of the call update.
        """
        try:
            ci = call_intent
            ct = self.get_call_type(call_intent)
            if ci == None:
                ci = "Other"
            print(f"UserID: {user_id} | Call Intent: {ci} | Call Type: {ct}")
            track_metrics(user_id, call_type=ct, call_intent=ci)
            print("Call tracked!")
        except Exception as e:
            return f"Error occurred: {str(e)}"
        return "Call status updated successfully."

    