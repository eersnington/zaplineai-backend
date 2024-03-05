from lib.call_chat import CallChatSession

def main():
    # Initialize the chat session with your Shopify app token and store name
    app_token = "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"
    myshopify = "zaplineai.myshopify.com"
    chat_session = CallChatSession(app_token, myshopify)

    # Simulate a conversation with the chatbot
    sid = "session_id_here"
    customer_phone_no = "+919952062221"
    chat_session.start(sid, customer_phone_no)

    while True:
        # Get user input
        message = input("You: ")

        # Break the loop if the user enters "exit"
        if message.lower() == "exit":
            break

        # Get the bot's response
        response = chat_session.get_response(message)
        print("Bot:", response)

if __name__ == "__main__":
    main()
