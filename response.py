import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

DEFAULT_SYSTEM_MESSAGE = "Ask for clarification in the email thread"

def generate_response(user_input, history=None):
    if history is None:
        history = [
            {"role": "system", "content": DEFAULT_SYSTEM_MESSAGE}
        ]
    
    history.append({
        "role": "user",
        "content": user_input,
    })
    
    print(f"Generating response for: {user_input}")
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-120B",
        messages=history,
    )

    assistant_message = response.choices[0].message.content
    history.append({
        "role": "assistant",
        "content": assistant_message
    })

    return assistant_message, history


if __name__ == "__main__":
    chat_history = None
    while True:
        user_input = input("You: ")
        if user_input.lower().strip() == "stop":
            print("Goodbye!")
            break
        response, chat_history = generate_response(user_input, history=chat_history)
        print(f"Assistant: {response}")

