import asyncio
import configparser
import json
from groq import Groq
from msgraph.generated.models.o_data_errors.o_data_error import ODataError
from graph import Graph


from main import get_mails
from response import generate_response

class SendEmail:        
    def __init__(self, email_address: str):
        self.email_address = email_address
    
    async def configure(self):
        config = configparser.ConfigParser()
        config.read(['config.cfg', 'config.dev.cfg'])
        if 'azure' not in config:
            raise ValueError("Azure settings not found in config files.")
        azure_settings = config['azure']

        graph: Graph = Graph(azure_settings)
        return graph

class EmailAgent:
    def __init__(self, groq_api_key: str, email_address: str):
        self.client = Groq(api_key=groq_api_key)
        self.email_service = SendEmail(email_address)
        self.email_address = email_address

    async def run(self, prompt: str):
        graph = await self.email_service.configure()
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "send_email",
                    "description": "Send an email to a specific recipient",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to": {
                                "type": "string",
                                "description": "The email address of the recipient"
                            },
                            "subject": {
                                "type": "string",
                                "description": "The subject of the email"
                            },
                            "body": {
                                "type": "string",
                                "description": "The body of the email"
                            }
                        },
                        "required": ["to", "subject", "body"]
                    }
                }
            }
        ]

        messages = [
            {
                "role": "system",
                "content": f"You are an assistant that can send emails using the Microsoft Graph API. The default recipient is {self.email_address} if none is specified."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-120B",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "send_email":
                    print(f"Sending email to {function_args.get('to')}...")
                    await graph.send_mail(
                        subject=function_args.get("subject"),
                        body=function_args.get("body"),
                        recipient=function_args.get("to")
                    )
                    print("Email sent successfully.")
        else:
            print(response_message.content)

if __name__ == "__main__":
    # For testing, you'll need to provide your Groq API Key
    import os
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    if not GROQ_API_KEY:
        print("Please set the GROQ_API_KEY environment variable.")
    else:
        agent = EmailAgent(GROQ_API_KEY, "admin@ai10x.dev")
        asyncio.run(agent.run("Send an email to admin@ai10x.dev with subject 'Test' and body 'Hello from Groq!'"))