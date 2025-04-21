from flask import Flask
from openai import OpenAI
import requests
import os
from dotenv import load_dotenv
import datetime
import time
from git import Repo
import shutil

# Load env variables
load_dotenv("a.env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_AUDIO_REPO")
BRANCH = os.getenv("GITHUB_AUDIO_BRANCH", "main")

client = OpenAI(api_key=OPENAI_API_KEY)
app = Flask(__name__)

def get_next_filename(prefix="line_", extension=".mp3"):
    files = [f for f in os.listdir(".") if f.startswith(prefix) and f.endswith(extension)]
    nums = [int(f[len(prefix):-len(extension)]) for f in files if f[len(prefix):-len(extension)].isdigit()]
    return f"{prefix}{max(nums, default=0) + 1:03d}{extension}"

def fetch_funding_news():
    query = "startup funding site:techcrunch.com OR site:crunchbase.com"
    params = {"engine": "google", "q": query, "tbm": "nws", "num": 3, "api_key": SERPAPI_API_KEY}
    res = requests.get("https://serpapi.com/search", params=params)
    if res.status_code != 200: return "No news."
    data = res.json().get("news_results", [])
    return "\n".join([f"- {x.get('title')} ({x.get('source')})" for x in data]) or "No funding news."

def generate_radio_line():
    news = fetch_funding_news()
    prompt = f"""
You are Johnny 'Jetstream' Blaze on Nomad FM.
Recap today’s startup funding news:
{news}
Use a sleazy 80s British rocker tone and keep it under 60 words so it fits within a 30-second audio clip.
Start with: "Live from Nomad FM"
End with: "This is Johnny 'Jetstream' Blaze on Nomad FM—broadcasting brilliance across borders. Don’t touch that dial."
"""
    chat = client.chat.completions.create(model="gpt-4", messages=[{"role": "system", "content": prompt}])
    line = chat.choices[0].message.content.strip()
    print(f"\n[GPT] 🎤 {line}\n")
    return line

def convert_to_speech(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
    payload = {"text": text, "voice_settings": {"stability": 0.4, "similarity_boost": 0.7}}
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code == 200:
        filename = get_next_filename()
        with open(filename, "wb") as f: f.write(res.content)
        print(f"[ElevenLabs] ✅ Saved '{filename}'")
        return filename
    else:
        print(f"[❌ ERROR] ElevenLabs: {res.status_code} - {res.text}")
        return None

def upload_to_github(filepath):
    repo_url = f"https://{GITHUB_TOKEN}:x-oauth-basic@github.com/{GITHUB_REPO}.git"
    temp_dir = "temp_audio_repo"
    Repo.clone_from(repo_url, temp_dir, branch=BRANCH)
    audio_dir = os.path.join(temp_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M")
    dest_filename = f"line_{ts}.mp3"
    dest_path = os.path.join(audio_dir, dest_filename)
    shutil.copy(filepath, dest_path)

    # Also update line_latest.mp3
    latest_path = os.path.join(audio_dir, "line_latest.mp3")
    shutil.copy(filepath, latest_path)

    repo = Repo(temp_dir)
    repo.git.add(A=True)
    repo.index.commit(f"Add radio line {ts} and update latest")
    repo.remote(name="origin").push()
    shutil.rmtree(temp_dir)
    print(f"[GitHub] ✅ Uploaded to {dest_path} and updated line_latest.mp3")

@app.route("/")
def run_pipeline():
    line = generate_radio_line()
    mp3 = convert_to_speech(line)
    if mp3: upload_to_github(mp3)
    return "✅ Radio line created."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

