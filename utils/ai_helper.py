import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_bio(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a creative assistant that writes short professional bios."},
            {"role": "user", "content": f"Write a short 1-liner professional bio based on: {prompt}"}
        ],
        max_tokens=50,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()
