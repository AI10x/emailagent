import asyncio
import os
import configparser
from graph import Graph
from main import list_inbox
from response import generate_response
from email_agent import EmailAgent

async def run_auto_responder():
    # Load settings
    config = configparser.ConfigParser()
    config.read(['config.cfg', 'config.dev.cfg'])
    if 'azure' not in config:
        print("Error: Azure settings not found in config files.")
        return
    azure_settings = config['azure']

    # Initialize Graph
    graph = Graph(azure_settings)

    # 1. Fetch emails
    print("Fetching inbox...")
    recipient_contents = await list_inbox(graph)

    if not recipient_contents:
        print("No threaded messages found to respond to.")
        return

    # Initialize EmailAgent
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        print("Error: GROQ_API_KEY environment variable not set.")
        return
    
    # We'll use a dummy address for construction, but the agent will use the one from the email
    agent = EmailAgent(groq_api_key, "auto-responder@example.com")

    for body, email_address_obj in recipient_contents:
        sender_email = email_address_obj.address
        print(f"\nProcessing email from: {sender_email}")
        print(f"Body: {body}")

        # 2. Prepare a response based on the body using response.py
        print("Generating response...")
        response_text = generate_response(body)
        print(f"Generated Response: {response_text}")
        while True:
            user_input = input("You: ")
            response = generate_response(user_input)
            if user_input.lower().strip() == "send & exit":
                print("Sending email - Goodbye!")
                break
            print(f"Assistant: {response}")
        # 3. Send the response to the email address via tool calling using email_agent.py
        # The prompt for the agent tells it what to do
        prompt = f"Send an email to {sender_email} with subject 'Re: Your message' and body '{response_text}'"
        print(f"Agent prompt: {prompt}")
        
        await agent.run(prompt)
        print(f"Finished processing for {sender_email}")

if __name__ == "__main__":
    asyncio.run(run_auto_responder())
