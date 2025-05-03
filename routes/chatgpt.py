from flask import Blueprint, request, jsonify
from services.chatgpt_service import ask_chatgpt
from services.supabase_client import supabase

chatgpt_blueprint = Blueprint('chatgpt', __name__)


@chatgpt_blueprint.route("/api/chatgpt/should-google", methods=["POST"])
def should_google():
    data = request.get_json()
    topic = data.get("topic")

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    prompt = f"Given the topic '{topic}', would it be helpful to search online for the latest news or facts before writing about it? Answer only 'yes' or 'no'. No explanation."

    try:
        answer = ask_chatgpt(prompt, temperature=0.0, max_tokens=5).lower()
        if answer not in ["yes", "no"]:
            answer = "no"
        return jsonify({"should_google": answer == "yes"})
    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"error": "Failed to call ChatGPT"}), 500


@chatgpt_blueprint.route("/api/chatgpt/generate-overview", methods=["POST"])
def generate_overview():
    data = request.get_json()
    topic = data.get("topic")

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    prompt = f"Write a simple, engaging 300-word overview about '{topic}'. Use clear, easy-to-understand language."

    try:
        overview = ask_chatgpt(prompt, temperature=0.5, max_tokens=600)

        # Save to Supabase
        supabase.table("topics").insert({"topic": topic, "overview": overview}).execute()

        return jsonify({"overview": overview})
    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"error": "Failed to generate overview"}), 500


@chatgpt_blueprint.route("/api/topics", methods=["GET"])
def get_topics():
    try:
        response = supabase.table("topics").select("*").order("created_at", desc=True).execute()
        return jsonify(response.data)
    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"error": "Failed to load topics"}), 500


@chatgpt_blueprint.route("/api/topics/<string:topic_name>", methods=["DELETE"])
def delete_topic(topic_name):
    try:
        supabase.table("topics").delete().eq("topic", topic_name).execute()
        return jsonify({"success": True})
    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"error": "Failed to delete topic"}), 500


@chatgpt_blueprint.route("/api/chatgpt/generate-line", methods=["POST"])
def generate_line():
    data = request.get_json()
    topic = data.get("topic")
    host_description = data.get("host_description")

    if not topic.strip() or not host_description.strip():
        return jsonify({"error": "Topic and Host Description are required"}), 400

    try:
        # Load all topics from Supabase
        topics = supabase.table("topics").select("*").execute().data
        matching_topic = next((t for t in topics if t["topic"] == topic), None)

        if not matching_topic:
            return jsonify({"error": "Topic overview not found."}), 400

        overview = matching_topic.get("overview", "")
        if not overview.strip():
            return jsonify({"error": "Topic overview is empty."}), 400

        prompt = (
            f"You are a radio host with this personality: {host_description}. "
            f"Here is the background for you to understand the topic:\n\n{overview}\n\n"
            "Now, ignoring all unnecessary details, reveal one fact about the topic. "
            "It should be around 150 characters long. Make sure the personality of the radio host is reflected in the line."
        )

        line = ask_chatgpt(prompt, temperature=0.7, max_tokens=200)
        return jsonify({"line": line})
    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"error": "Failed to generate line"}), 500