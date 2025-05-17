import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

BASE_URL_V1 = "https://api.elevenlabs.io/v1"
BASE_URL_V2 = "https://api.elevenlabs.io/v2"

HEADERS = {
    "xi-api-key": ELEVENLABS_API_KEY,
    "Accept": "application/json"
}


# ---- V1 APIs ---- #

# This function creates a voice using the ElevenLabs API.
def create_voice(name, description):
    preview_url = f"{BASE_URL_V1}/text-to-voice/create-previews"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    
    #Preview Payload should be adjusted to be shorter for more efficient resource utilization. 
    #It should also be post this info for choosing which voice to use. Maybe in a popup during generation.
    preview_payload = {
        "voice_description": description,
        "text": (
            "The sun was setting on the horizon, casting long shadows across the bustling cityscape. "
            "In the distance, the sound of traffic mingled with the gentle rustling of leaves in the evening breeze. "
            "A perfect moment to reflect on the day's events and share stories with friends and family. "
            "The world seemed to slow down, if only for a moment, as the sky painted itself in brilliant hues of orange and purple."
        )
    }
    
    preview_response = requests.post(preview_url, headers=headers, json=preview_payload)
    
    if preview_response.status_code != 200:
        print(f"[❌ ERROR] Generate Previews: {preview_response.status_code} - {preview_response.text}")
        return None

    previews = preview_response.json().get("previews", [])
    if not previews:
        print("[❌ ERROR] No previews generated")
        return None

    generated_voice_id = previews[0]["generated_voice_id"]

    create_url = f"{BASE_URL_V1}/text-to-voice/create-voice-from-preview"
    create_payload = {
        "voice_name": name,
        "voice_description": description,
        "generated_voice_id": generated_voice_id
    }
    
    create_response = requests.post(create_url, headers=headers, json=create_payload)
    
    if create_response.status_code in [200, 201]:
        voice = create_response.json()
        print(f"[ElevenLabs] ✅ Created voice '{name}' with ID: {voice.get('voice_id')}")
        return voice
    else:
        print(f"[❌ ERROR] Create Voice from Preview: {create_response.status_code} - {create_response.text}")
        return None

# This function deletes a voice using its ID.
def delete_voice(voice_id):
    url = f"{BASE_URL_V1}/voices/{voice_id}"  
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY
    }

    response = requests.delete(url, headers=headers)

    if response.status_code == 200:  
        print(f"[ElevenLabs] ✅ Deleted voice with ID: {voice_id}")
        return True
    else:
        print(f"[❌ ERROR] Delete Voice: {response.status_code} - {response.text}")
        return False

# This function retrieves the details of a specific voice using its ID. Needed for Description.
def get_voice_details(voice_id):
    url = f"{BASE_URL_V1}/voices/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        voice_data = response.json()
        return voice_data
    else:
        print(f"[❌ ERROR] Get Voice Details: {response.status_code} - {response.text}")
        return None



def generate_voice_line(voice_id, text):
    url = f"{BASE_URL_V1}/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.content  # MP3 bytes
    else:
        print(f"[❌ ERROR] TTS API: {response.status_code} - {response.text}")
        return None



def save_voice_file(mp3_content, filename):
    save_path = os.path.join("static", "audio", filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    with open(save_path, "wb") as f:
        f.write(mp3_content)

    print(f"[✅] Saved voice line to {save_path}")
    return save_path


# ---- V2 APIs ---- #

# This function lists Clones and Generated voices available in the ElevenLabs API.
def list_voices():
    url = f"{BASE_URL_V2}/voices"
    headers = {
        "Accept": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    voices = []
    
    cloned_response = requests.get(url, headers=headers, params={"category": "cloned"})
    if cloned_response.status_code == 200:
        cloned_voices = cloned_response.json().get("voices", [])
        voices.extend(cloned_voices)
        
    design_response = requests.get(url, headers=headers, params={"category": "generated"})
    if design_response.status_code == 200:
        design_voices = design_response.json().get("voices", [])
        voices.extend(design_voices)
        
    return voices