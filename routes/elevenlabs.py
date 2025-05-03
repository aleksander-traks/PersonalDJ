from flask import Blueprint, render_template, request, jsonify
from pydub import AudioSegment
import imageio_ffmpeg  # ✅ Use this instead of ffmpeg-static
from services.elevenlabs.hosts import (
    list_voices,
    create_voice,
    delete_voice,
    get_voice_details,
    generate_voice_line,
    save_voice_file
)
import time
import os

# Blueprint setup
elevenlabs_blueprint = Blueprint('elevenlabs', __name__)

# Homepage
@elevenlabs_blueprint.route("/")
def homepage():
    return render_template("index.html")

# Get all hosts (voices)
@elevenlabs_blueprint.route("/api/hosts", methods=["GET"])
def get_hosts():
    voices = list_voices()
    enriched_voices = []

    for voice in voices:
        voice_id = voice.get("voice_id")
        name = voice.get("name", "Unnamed Voice")
        
        details = get_voice_details(voice_id)
        
        description = ""
        if details:
            description = details.get("description", "")
        
        enriched_voices.append({
            "voice_id": voice_id,
            "name": name,
            "description": description
        })

    return jsonify(enriched_voices)

# Add a new host
@elevenlabs_blueprint.route("/api/hosts", methods=["POST"])
def add_host():
    data = request.get_json()
    name = data.get("name", "").strip()
    description = data.get("description", "").strip()

    if not name or not description:
        return jsonify({"error": "Name and description are required"}), 400

    voice = create_voice(name, description)
    if voice:
        return jsonify({"success": True, "voice_id": voice.get("voice_id")})
    else:
        return jsonify({"error": "Failed to create voice"}), 500

# Delete a host
@elevenlabs_blueprint.route("/api/hosts/<voice_id>", methods=["DELETE"])
def delete_host(voice_id):
    success = delete_voice(voice_id)
    if success:
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Failed to delete voice"}), 500

# Generate a voice line
@elevenlabs_blueprint.route("/api/elevenlabs/generate-audio", methods=["POST"])
def generate_audio():
    data = request.get_json()
    voice_id = data.get("voice_id")
    host_name = data.get("host_name")
    topic_name = data.get("topic_name")
    text = data.get("text")
    music_intro = data.get("music_intro")

    if not voice_id or not host_name or not topic_name or not text:
        return jsonify({"error": "Missing fields."}), 400

    mp3_content = generate_voice_line(voice_id, text)
    if not mp3_content:
        return jsonify({"error": "Failed to generate voice line."}), 500

    # Create filenames
    safe_host = host_name.replace(" ", "_")
    safe_topic = topic_name.replace(" ", "_")
    voice_filename = f"{safe_host}+{safe_topic}+voice.mp3"
    final_filename = f"{safe_host}+{safe_topic}+final.mp3"

    voice_path = save_voice_file(mp3_content, voice_filename)

    if music_intro:
        try:
            intro_path = os.path.join("static", "audio", "soundbite", music_intro)
            print(f"[DEBUG] Intro path: {intro_path}")
            print(f"[DEBUG] File exists: {os.path.exists(intro_path)}")

            intro_audio = AudioSegment.from_mp3(intro_path)
            print(f"[DEBUG] Intro audio duration: {len(intro_audio)} ms")

            voice_audio = AudioSegment.from_file(voice_path)
            print(f"[DEBUG] Voice audio duration: {len(voice_audio)} ms")

            combined = intro_audio + voice_audio
            final_path = os.path.join("static", "audio", final_filename)
            combined.export(final_path, format="mp3")

            return jsonify({"audio_url": f"/static/audio/{final_filename}"})
        except Exception as e:
            print("[ERROR] Audio merging failed:", e)
            return jsonify({"error": "Failed to merge intro and voice line."}), 500
    else:
        return jsonify({"audio_url": f"/static/audio/{voice_filename}"})