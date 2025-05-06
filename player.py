from flask import Blueprint, jsonify, request
from flask_cors import CORS  # ✅ Add this
from supabase import create_client
import os

player_blueprint = Blueprint('player', __name__)
CORS(player_blueprint)  # ✅ Enable CORS for this blueprint

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
        return jsonify([])

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

# ✅ GET /api/voice-lines/<filename>/url
# Returns a signed URL for the selected MP3
@player_blueprint.route("/api/voice-lines/<filename>/url", methods=["GET"])
def get_audio_file_url(filename):
    try:
        signed_url_data = supabase.storage.from_(SUPABASE_BUCKET).create_signed_url(filename, 60)
        if not signed_url_data or "signedURL" not in signed_url_data:
            raise Exception("Failed to get signed URL")
        return jsonify({"url": signed_url_data["signedURL"]})
    except Exception as e:
        print("[ERROR] Failed to generate signed URL:", e)
        return jsonify({"error": "Unable to generate file URL"}), 500