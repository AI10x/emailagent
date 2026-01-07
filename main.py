# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# <ProgramSnippet>
import asyncio
import configparser
from msgraph.generated.models.o_data_errors.o_data_error import ODataError
from graph import Graph




# Load settings
config = configparser.ConfigParser()
config.read(['config.cfg', 'config.dev.cfg'])
azure_settings = config['azure']

graph: Graph = Graph(azure_settings)

async def main():
    print('Python Graph Tutorial\n')

    # Load settings
    config = configparser.ConfigParser()
    config.read(['config.cfg', 'config.dev.cfg'])
    azure_settings = config['azure']

    graph: Graph = Graph(azure_settings)

    await greet_user(graph)

    choice = -1

    while choice != 0:
        print('Please choose one of the following options:')
        print('0. Exit')
        print('1. Display access token')
        print('2. List my inbox')
        print('3. Send mail')
        print('4. Make a Graph call')

        try:
            choice = int(input())
        except ValueError:
            choice = -1

        try:
            if choice == 0:
                print('Goodbye...')
            elif choice == 1:
                await display_access_token(graph)
            elif choice == 2:
                await list_inbox(graph)
            elif choice == 3:
                await send_mail(graph)
            elif choice == 4:
                await make_graph_call(graph)
            else:
                print('Invalid choice!\n')
        except ODataError as odata_error:
            print('Error:')
            if odata_error.error:
                print(odata_error.error.code, odata_error.error.message)
# </ProgramSnippet>

# <GreetUserSnippet>
async def greet_user(graph: Graph):
    user = await graph.get_user()
    if user:
        print('Hello,', user.display_name)
        # For Work/school accounts, email is in mail property
        # Personal accounts, email is in userPrincipalName
        print('Email:', user.mail or user.user_principal_name, '\n')
# </GreetUserSnippet>

# <DisplayAccessTokenSnippet>
async def display_access_token(graph: Graph):
    token = await graph.get_user_token()
    print('User token:', token, '\n')
# </DisplayAccessTokenSnippet>


inbox = []

# <ListInboxSnippet>
async def list_inbox(graph: Graph):
    message_page = await graph.get_inbox()
    if message_page and message_page.value:
        # Count conversationIds to identify threads
        conversation_counts = {}
        for message in message_page.value:
            cid = message.conversation_id
            conversation_counts[cid] = conversation_counts.get(cid, 0) + 1

        recepient_contents = []
        # Output each message's details only if it's part of a thread
        for message in message_page.value:
            if conversation_counts[message.conversation_id] > 1:
                print('Message:', message.subject)
                if (
                    message.from_ and
                    message.from_.email_address
                ):
                    print('  From:', message.from_.email_address.name or 'NONE')
                    print('  Body:', message.body_preview)
                    recepient_contents.append((message.body_preview, message.from_.email_address))
                else:
                    print('  From: NONE')
                print('  Status:', 'Read' if message.is_read else 'Unread')
                print('  Received:', message.received_date_time)
                print('  Conversation ID:', message.conversation_id)

        # If @odata.nextLink is present
        more_available = message_page.odata_next_link is not None
        print('\nMore messages available?', more_available, '\n')
        inbox.append(recepient_contents)
        return(recepient_contents)
# </ListInboxSnippet>

# <SendMailSnippet>
async def send_mail(graph: Graph):
    # Send mail to the signed-in user
    # Get the user for their email address
    user = await graph.get_user()
    if user:
        user_email = user.mail or user.user_principal_name

        await graph.send_mail('Testing Microsoft Graph', 'Hello world!', user_email or '')
        print('Mail sent.\n')
# </SendMailSnippet>

# <MakeGraphCallSnippet>
async def make_graph_call(graph: Graph):
    await graph.make_graph_call()
# </MakeGraphCallSnippet>






def get_mails():
    # Run main
    asyncio.run(list_inbox(graph))


    for page in inbox:
        for body, email in page:
            print(f"Body: {body}")
            print(f"Email: {email.address}")