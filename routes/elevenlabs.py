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
from io import BytesIO
import time
import os
from services.supabase_client import supabase

# Blueprint setup
elevenlabs_blueprint = Blueprint('elevenlabs', __name__)
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "audio")


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
        description = details.get("description", "") if details else ""

        enriched_voices.append({
            "voice_id": voice_id,
            "name": name,
            "description": description
        })

    return jsonify(enriched_voices)


#Fetches music intros from Supabase.
#This should be moved to it's own file
@elevenlabs_blueprint.route("/api/music-intros", methods=["GET"])
def list_music_intros():
    try:
        response = supabase.storage.from_("audio").list("soundbite")
        intros = [file["name"] for file in response if file["name"].endswith(".mp3")]
        return jsonify(intros)
    except Exception as e:
        print("[ERROR] Failed to fetch music intros:", e)
        return jsonify([])


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


# Generate a voice line (with optional intro)
@elevenlabs_blueprint.route("/api/elevenlabs/generate-audio", methods=["POST"])
def generate_audio():
    data = request.get_json()
    print("[INFO] Incoming request to /generate-audio:", data)

    voice_id = data.get("voice_id")
    host_name = data.get("host_name")
    topic_name = data.get("topic_name")
    text = data.get("text")
    music_intro = data.get("music_intro")

    if not voice_id or not host_name or not topic_name or not text:
        print("[ERROR] Missing required fields:", {
            "voice_id": voice_id,
            "host_name": host_name,
            "topic_name": topic_name,
            "text": text
        })
        return jsonify({"error": "Missing fields."}), 400

    try:
        mp3_content = generate_voice_line(voice_id, text)
        if not mp3_content:
            print("[ERROR] generate_voice_line returned empty content")
            return jsonify({"error": "Failed to generate voice line."}), 500
    except Exception as e:
        print("[ERROR] Exception during voice generation:", e)
        return jsonify({"error": "Voice generation failed."}), 500

    safe_host = host_name.replace(" ", "_")
    safe_topic = topic_name.replace(" ", "_")
    final_filename = f"{safe_host}+{safe_topic}+final.mp3"

    try:
        voice_audio = AudioSegment.from_file(BytesIO(mp3_content), format="mp3")
    except Exception as e:
        print("[ERROR] Failed to load MP3 content:", e)
        return jsonify({"error": "Invalid MP3 content."}), 500

    if music_intro:
        try:
            intro_file_path = f"soundbite/{music_intro}"
            print("[INFO] Downloading intro from Supabase:", intro_file_path)
            intro_bytes = supabase.storage.from_(SUPABASE_BUCKET).download(intro_file_path)
            intro_audio = AudioSegment.from_file(BytesIO(intro_bytes), format="mp3")
            combined = intro_audio + voice_audio
        except Exception as e:
            print("[ERROR] Audio merging failed:", e)
            return jsonify({"error": "Failed to merge intro and voice line."}), 500
    else:
        combined = voice_audio

    buffer = BytesIO()
    try:
        combined.export(buffer, format="mp3")
        buffer.seek(0)
    except Exception as e:
        print("[ERROR] Failed to export combined audio:", e)
        return jsonify({"error": "Audio export failed."}), 500

    try:
        print("[INFO] Uploading to Supabase:", final_filename)
        buffer.seek(0)
        audio_bytes = buffer.read()
        supabase.storage.from_(SUPABASE_BUCKET).upload(final_filename, audio_bytes, {
            "content-type": "audio/mpeg"
        })
    except Exception as e:
        print("[ERROR] Supabase upload failed:", e)
        return jsonify({"error": "Upload to Supabase failed."}), 500

    public_url = f"{os.getenv('SUPABASE_URL')}/storage/v1/object/public/{SUPABASE_BUCKET}/{final_filename}"
    print("[SUCCESS] Audio available at:", public_url)
    return jsonify({"audio_url": public_url})


# Delete an audio file from Supabase
@elevenlabs_blueprint.route("/api/voice-lines/<filename>", methods=["DELETE"])
def delete_voice_line(filename):
    try:
        print(f"[INFO] Request to delete: {filename}")
        supabase.storage.from_(SUPABASE_BUCKET).remove([filename])
        return jsonify({"success": True})
    except Exception as e:
        print("[ERROR] Failed to delete audio file:", e)
        return jsonify({"error": "Failed to delete file"}), 500