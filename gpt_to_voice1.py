from openai import OpenAI
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("a.env")

# Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# Set up OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Rotate filenames
def get_next_filename(directory=".", prefix="line_", extension=".mp3"):
    files = [f for f in os.listdir(directory) if f.startswith(prefix) and f.endswith(extension)]
    existing_nums = [int(f[len(prefix):-len(extension)]) for f in files if f[len(prefix):-len(extension)].isdigit()]
    next_num = max(existing_nums, default=0) + 1
    return f"{prefix}{next_num:03d}{extension}"

# Fetch funding news via SerpAPI
def fetch_funding_news_from_serpapi():
    query = "startup funding site:techcrunch.com OR site:crunchbase.com"
    url = "https://serpapi.com/search"

    params = {
        "engine": "google",
        "q": query,
        "tbm": "nws",
        "num": 5,
        "api_key": SERPAPI_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("❌ Failed to fetch news:", response.text)
        return "No funding news could be retrieved today."

    data = response.json()
    news_results = data.get("news_results", [])

    if not news_results:
        print("⚠️ No news results found.")
        return "No funding news could be retrieved today."

    formatted_news = ""
    for article in news_results:
        title = article.get("title", "No Title")
        snippet = article.get("snippet", "No description available.")
        source = article.get("source", "Unknown Source")
        date = article.get("date", "Unknown Date")
        formatted_news += f"- {title} ({source}, {date}): {snippet}\n"

    print("📰 News fetched successfully:\n")
    print(formatted_news)
    return formatted_news.strip()

# Generate Jetstream voice line
def generate_radio_line():
    funding_news = fetch_funding_news_from_serpapi()

    prompt = f"""
You are Johnny 'Jetstream' Blaze, the charismatic British rocker and host of Nomad FM, an 80s-inspired digital radio station.

Each day, you deliver a punchy, under-60-second segment highlighting the most intriguing startup funding news from the previous day.

Here are the funding stories:

{funding_news}

Infuse your narration with 80s flair, cheeky British wit, and energetic delivery, making the news sound like breaking rock 'n roll updates.

Conclude each segment with your signature sign-off: "This is Johnny 'Jetstream' Blaze on Nomad FM—broadcasting brilliance across borders. Don’t touch that dial."
"""

    chat = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )

    line = chat.choices[0].message.content.strip()
    print(f"\n[GPT] 🎤 {line}\n")
    return line

# Convert to speech & save with rotating filename
def convert_to_speech(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.7
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        filename = get_next_filename()
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"[ElevenLabs] ✅ Voice saved as '{filename}'")
    else:
        print(f"[❌ ERROR] ElevenLabs said: {response.status_code} - {response.text}")

# Run
if __name__ == "__main__":
    line = generate_radio_line()
    convert_to_speech(line)
