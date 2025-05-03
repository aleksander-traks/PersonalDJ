from flask import Blueprint, request, jsonify
from services.chatgpt_client import generate_topic_overview  # Assumes you have this
from services.supabase_client import supabase

topics_blueprint = Blueprint('topics', __name__)

# GET all topics (assumes stored in a Supabase table or JSON file)
@topics_blueprint.route("/api/topics", methods=["GET"])
def get_topics():
    try:
        response = supabase.table("topics").select("*").execute()
        return jsonify(response.data or [])
    except Exception as e:
        print("[ERROR] Failed to load topics:", e)
        return jsonify([])


# POST - Generate overview and store topic
@topics_blueprint.route("/api/chatgpt/generate-overview", methods=["POST"])
def generate_overview():
    data = request.get_json()
    topic = data.get("topic", "").strip()

    if not topic:
        return jsonify({"error": "Missing topic"}), 400

    try:
        overview = generate_topic_overview(topic)
        supabase.table("topics").insert({"topic": topic, "overview": overview}).execute()
        return jsonify({"topic": topic, "overview": overview})
    except Exception as e:
        print("[ERROR] Failed to generate or store overview:", e)
        return jsonify({"error": "Failed to process topic"}), 500


# DELETE topic by name
@topics_blueprint.route("/api/topics/<topic_name>", methods=["DELETE"])
def delete_topic(topic_name):
    try:
        print(f"[INFO] Deleting topic: {topic_name}")
        response = supabase.table("topics").delete().eq("topic", topic_name).execute()
        return jsonify({"success": True})
    except Exception as e:
        print("[ERROR] Failed to delete topic:", e)
        return jsonify({"error": "Failed to delete topic"}), 500