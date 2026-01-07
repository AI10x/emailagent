import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

messages = [
    {
        "role": "system",
        "content": "Ask for clarification in the email thread"
    }
]


def generate_response(user_input):
    messages.append({
        "role": "user",
        "content": user_input,
    })
    print(user_input)
    response = client.chat.completions.create(
        model="openai/gpt-oss-120B",
        messages=messages,
    )

    assistant_message = response.choices[0].message.content
    messages.append({
        "role": "assistant",
        "content": assistant_message
    })

    return assistant_message


if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower().strip() == "stop":
            print("Goodbye!")
            break
        response = generate_response(user_input)
        print(f"Assistant: {response}")

