from lib.call_chat import CallChatSession

def main():
    # Initialize the chat session with your Shopify app token and store name
    app_token = "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"
    myshopify = "b59bb6-2.myshopify.com"
    chat_session = CallChatSession(app_token, myshopify)

    # Simulate a conversation with the chatbot
    sid = "session_id_here"
    customer_phone_no = "+12512209809"
    chat_session.start(sid, customer_phone_no)

    call_intent = None

    awaited_response, order_id = chat_session.start(sid, customer_phone_no)
    print("Bot:", awaited_response)


    while True:
        # Get user input
        message = input("You: ")

        # Break the loop if the user enters "exit"
        if message.lower() == "exit":
            break

        if order_id is not None:
            bot_response = "Would you like to know the status of the order, process a return, or something else?"
            print("Bot:", bot_response)
            order_id = None
            continue

        if call_intent is None:
            call_intent = chat_session.check_call_intent(message)
            call_type = chat_session.get_call_type(call_intent=call_intent)

            print(f"Call Intent: {call_intent} | Call Type: {call_type}")

        # Get the bot's response
        response = chat_session.get_response(message)
        print("Bot:", response)

if __name__ == "__main__":
    main()
