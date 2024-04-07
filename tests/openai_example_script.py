import os
from reprompt import start_trace
from openai import OpenAI

# Replace 'your_api_key_here' with your actual OpenAI API key
API_KEY = os.getenv("OPENAI_API_KEY") or "your_api_key_here"


def main():
    start_trace(API_KEY)

    client = OpenAI()
    OpenAI.api_key = API_KEY

    completion = client.completions.create(
        model="gpt-3.5-turbo-instruct", prompt="Say this is a test", max_tokens=7, temperature=0
    )

    print(completion.choices[0].text)


if __name__ == "__main__":
    main()
