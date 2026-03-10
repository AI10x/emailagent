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

    for body, email_address_obj, msg_id in recipient_contents:
        sender_email = email_address_obj.address
        sender_name = email_address_obj.name or "Unknown"
        print(f"\n--- Found message from {sender_name} ({sender_email}) ---")
        
        # 1. Check if the user wants to respond to this sender
        confirm_respond = input(f"Would you like to prepare a response for {sender_email}? (y/n): ").strip().lower()
        if confirm_respond != 'y':
            print(f"Skipping {sender_email}.")
            continue

        # 2. Prepare a response draft based on the body using response.py
        print("\nGenerating draft response...")
        current_draft, chat_history = generate_response(body)
        
        while True:
            print("-" * 30)
            print(f"CURRENT DRAFT:\n{current_draft}")
            print("-" * 30)
            
            # 3. Interactive Menu
            print("\nOptions: (s)end, (e)dit draft, (d)iscard")
            user_choice = input("Choice: ").strip().lower()
            
            if user_choice == 's':
                # 4. Reply via EmailAgent using the message_id
                prompt = f"Reply to the email with message_id '{msg_id}' to recipient {sender_email} with body: {current_draft}"
                print(f"Sending via AI Agent...")
                await agent.run(prompt)
                print(f"Finished processing and sent to {sender_email}")
                break
            elif user_choice == 'e':
                # Refine the draft with AI
                edit_instruction = input("How should I change the draft? (e.g., 'make it shorter'): ").strip()
                if edit_instruction:
                    print("\nRefining draft...")
                    current_draft, chat_history = generate_response(edit_instruction, history=chat_history)
                else:
                    print("No instruction provided. Returning to menu.")
            elif user_choice == 'd':
                print(f"Draft for {sender_email} was discarded.")
                break
            else:
                print("Invalid choice. Please select (s), (e), or (d).")

if __name__ == "__main__":
    asyncio.run(run_auto_responder())
