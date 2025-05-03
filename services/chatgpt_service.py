import openai
import os
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # ✅ NEW way

def ask_chatgpt(prompt, model="gpt-4o", temperature=0.0, max_tokens=1000):
    response = client.chat.completions.create(   # ✅ NEW way
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()