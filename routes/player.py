from flask import Blueprint, jsonify, request
from supabase import create_client
import os

player_blueprint = Blueprint('player', __name__)

# Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "audio")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ✅ GET /api/voice-lines
# Lists all MP3s from Supabase Storage
@player_blueprint.route("/api/voice-lines", methods=["GET"])
def list_audio_files():
    try:
        response = supabase.storage.from_(SUPABASE_BUCKET).list()
        if not isinstance(response, list):
            raise Exception("Invalid response from Supabase Storage")

        files = [file["name"] for file in response if isinstance(file, dict) and file.get("name", "").endswith(".mp3")]
        return jsonify(files)
    except Exception as e:
        print("[ERROR] Failed to fetch audio files:", e)
        return jsonify([])  # Return empty array instead of error


# ✅ DELETE /api/voice-lines/<filename>
# Deletes a specific MP3 from Supabase Storage
@player_blueprint.route("/api/voice-lines/<filename>", methods=["DELETE"])
def delete_audio_file(filename):
    try:
        result = supabase.storage.from_(SUPABASE_BUCKET).remove([filename])
        return jsonify({"success": True})
    except Exception as e:
        print("[ERROR] Failed to delete audio file:", e)
        return jsonify({"error": "Unable to delete file"}), 500