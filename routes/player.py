from flask import Blueprint, jsonify
import os

# Create a new blueprint for the player
player_blueprint = Blueprint('player', __name__)

# Define the /api/voice-lines route
@player_blueprint.route("/api/voice-lines", methods=["GET"])
def list_voice_lines():
    audio_folder = os.path.join("static", "audio")
    try:
        files = os.listdir(audio_folder)
        audio_files = [f for f in files if f.endswith(".mp3")]
        return jsonify({"audio_files": audio_files})
    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"error": "Failed to list audio files"}), 500


# Define the /api/music-intros route 
@player_blueprint.route("/api/music-intros", methods=["GET"])
def list_music_intros():
    audio_folder = os.path.join("static", "audio", "soundbite")
    try:
        files = os.listdir(audio_folder)
        audio_files = [f for f in files if f.endswith(".mp3")]
        return jsonify({"intros": audio_files})
    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"error": "Failed to list music intros"}), 500
