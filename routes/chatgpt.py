from flask import Blueprint, request, jsonify
from services.chatgpt_service import ask_chatgpt
from services.topic_storage import load_topics, save_topics

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
        
        # 🛠 Save new topic
        topics = load_topics()
        topics.append({
            "topic": topic,
            "overview": overview
        })
        save_topics(topics)

        return jsonify({"overview": overview})
    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"error": "Failed to generate overview"}), 500

@chatgpt_blueprint.route("/api/topics", methods=["GET"])
def get_topics():
    try:
        topics = load_topics()
        return jsonify(topics)
    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"error": "Failed to load topics"}), 500

@chatgpt_blueprint.route("/api/topics/<string:topic_name>", methods=["DELETE"])
def delete_topic(topic_name):
    try:
        topics = load_topics()
        topics = [t for t in topics if t["topic"] != topic_name]
        save_topics(topics)
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

    # 🛠 Load all saved topics
    topics = load_topics()
    # 🛡️ Try to find the matching overview
    matching_topic = next((t for t in topics if t["topic"] == topic), None)

    if not matching_topic:
        return jsonify({"error": "Topic overview not found."}), 400

    overview = matching_topic.get("overview", "")

    if not overview.strip():
        return jsonify({"error": "Topic overview is empty."}), 400

    prompt = (
        f"You are a radio host with this personality: {host_description}. "
        f"Here is the background for you to understand the topic:\n\n{overview}\n\n"
        "Now, ignoring all unnecessary details, reveal one fact about the topic, It should be around 150 characters long. Make sure the personality of the radio host is reflected in the line. "
    )

    try:
        line = ask_chatgpt(prompt, temperature=0.7, max_tokens=200)
        return jsonify({"line": line})
    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"error": "Failed to generate line"}), 500