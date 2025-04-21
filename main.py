# Import required libraries
from flask import Flask, render_template  # For web interface
from openai import OpenAI  # To interact with ChatGPT
import requests  # For API calls
import os  # For environment variables
from dotenv import load_dotenv  # To load .env secrets
import datetime  # To generate timestamps
import time
from git import Repo  # To interact with GitHub repo
import shutil  # For file operations

# Load environment variables from a.env file
load_dotenv("a.env")

# API Keys and config from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_AUDIO_REPO")  # Format: username/repo
BRANCH = os.getenv("GITHUB_AUDIO_BRANCH", "main")

# Setup OpenAI client and Flask app
client = OpenAI(api_key=OPENAI_API_KEY)
app = Flask(__name__, template_folder="templates")

# Generate a unique filename for each MP3 line
def get_next_filename(prefix="line_", extension=".mp3"):
    files = [f for f in os.listdir(".") if f.startswith(prefix) and f.endswith(extension)]
    nums = [int(f[len(prefix):-len(extension)]) for f in files if f[len(prefix):-len(extension)].isdigit()]
    return f"{prefix}{max(nums, default=0) + 1:03d}{extension}"

# Get recent startup funding news from SerpAPI
def fetch_funding_news():
    query = "startup funding site:techcrunch.com OR site:crunchbase.com"
    params = {"engine": "google", "q": query, "tbm": "nws", "num": 3, "api_key": SERPAPI_API_KEY}
    res = requests.get("https://serpapi.com/search", params=params)
    if res.status_code != 200: return "No news."
    data = res.json().get("news_results", [])
    return "\n".join([f"- {x.get('title')} ({x.get('source')})" for x in data]) or "No funding news."

# Use GPT to generate a short 80s-style radio line
def generate_radio_line():
    news = fetch_funding_news()
    prompt = f"""
You are Johnny 'Jetstream' Blaze on Nomad FM.
Recap today’s startup funding news:
{news}
Use a sleazy 80s British rocker tone and keep it under 60 words so it fits within a 30-second audio clip.
Start with: "Coming in from Nomad FM"
End with: "This is Johnny 'Jetstream' Blaze on Nomad FM—broadcasting brilliance across borders. Don’t touch that dial."
"""
    chat = client.chat.completions.create(model="gpt-4", messages=[{"role": "system", "content": prompt}])
    line = chat.choices[0].message.content.strip()
    print(f"\n[GPT] 🎤 {line}\n")
    return line

# Convert generated text to MP3 using ElevenLabs API
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

# Upload MP3 to GitHub Pages repo
def upload_to_github(filepath):
    repo_url = f"https://{GITHUB_TOKEN}:x-oauth-basic@github.com/{GITHUB_REPO}.git"
    temp_dir = "temp_audio_repo"

    # Clone repo
    Repo.clone_from(repo_url, temp_dir, branch=BRANCH)
    audio_dir = os.path.join(temp_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    # Generate filename with timestamp
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M")
    dest_filename = f"line_{ts}.mp3"
    dest_path = os.path.join(audio_dir, dest_filename)
    shutil.copy(filepath, dest_path)

    # Also update the file 'line_latest.mp3' as a stable URL for the latest clip
    latest_path = os.path.join(audio_dir, "line_latest.mp3")
    shutil.copy(filepath, latest_path)

    # Commit & push changes
    repo = Repo(temp_dir)
    repo.git.add(A=True)
    repo.index.commit(f"Add radio line {ts} and update latest")
    repo.remote(name="origin").push()
    shutil.rmtree(temp_dir)
    print(f"[GitHub] ✅ Uploaded to {dest_path} and updated line_latest.mp3")

# Home route — serves button UI
@app.route("/")
def homepage():
    return render_template("index.html")

# Run pipeline only when this route is triggered manually (by button click)
@app.route("/run")
def run_pipeline():
    line = generate_radio_line()
    mp3 = convert_to_speech(line)
    if mp3: upload_to_github(mp3)
    return "✅ Radio line created and uploaded."

# Start the Flask app on port 10000
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

