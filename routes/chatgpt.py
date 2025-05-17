from flask import Blueprint, request, jsonify
from services.chatgpt_service import ask_chatgpt
from services.supabase_client import supabase
from services.serpapi import fetch_serp_news

chatgpt_blueprint = Blueprint('chatgpt', __name__)
    

#stays same
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

#retrieve topic from Supabase
@chatgpt_blueprint.route("/api/topics", methods=["GET"])
def get_topics():
    try:
        response = supabase.table("topics").select("*").order("created_at", desc=True).execute()
        return jsonify(response.data)
    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"error": "Failed to load topics"}), 500

#Delete topic from Supabase
@chatgpt_blueprint.route("/api/topics/<string:topic_name>", methods=["DELETE"])
def delete_topic(topic_name):
    try:
        supabase.table("topics").delete().eq("topic", topic_name).execute()
        return jsonify({"success": True})
    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"error": "Failed to delete topic"}), 500

#Generate the line,
@chatgpt_blueprint.route("/api/chatgpt/generate-line", methods=["POST"])
def generate_line():
    data = request.get_json()
    topic = data.get("topic")
    host_description = data.get("host_description")

    if not topic.strip() or not host_description.strip():
        return jsonify({"error": "Topic and Host Description are required"}), 400

    try:
        # Load topic overview
        topics = supabase.table("topics").select("*").execute().data
        matching_topic = next((t for t in topics if t["topic"] == topic), None)
        if not matching_topic:
            return jsonify({"error": "Topic overview not found."}), 400

        overview = matching_topic.get("overview", "")
        if not overview.strip():
            return jsonify({"error": "Topic overview is empty."}), 400

        # Fetch last 15 lines
        recent_lines_response = supabase.table("lines") \
            .select("line") \
            .eq("topic", topic) \
            .order("created_at", desc=True) \
            .limit(15) \
            .execute()
        previous_lines = [entry["line"] for entry in recent_lines_response.data]

        print("[DEBUG] Previously stored lines:")
        for line in previous_lines:
            print("-", line)

        # Fetch SERP data
        serp_snippets = fetch_serp_news(topic)
        use_serp = serp_snippets and len(serp_snippets) >= 2
        serp_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(serp_snippets)])

        # History block for angle suggestion
        history_block = ""
        if previous_lines:
            history_block = (
            "Here are previously used lines:\n" +
            "\n".join([f"- {line}" for line in previous_lines]) +
            "\n\nYour task: Identify the key topics or facts covered in these lines (e.g. Bitcoin at $103k, Ethereum dip, Ripple ETF uncertainty). "
            "You are NOT allowed to mention or reference any of these topics again. Do NOT rephrase them. Do NOT frame them differently. "
            "Choose a completely different fact or angle from today's news."
    )

        # Build final prompt
        if use_serp:
            prompt = (
                f"You are a radio host with this personality: {host_description}.\n\n"
                f"Here is the background for you to understand the topic:\n\n{overview}\n\n"
                f"{history_block}"
                f"Here are today's real-time news headlines:\n{serp_text}\n\n"
                "Now, ignoring all unnecessary details, reveal one interesting fact. "
                "It should be around 150 characters long. Make sure the personality of the radio host is reflected."
            )
        else:
            prompt = (
                f"You are a radio host with this personality: {host_description}.\n\n"
                f"Here is the background for you to understand the topic:\n\n{overview}\n\n"
                f"{history_block}"
                "Now, reveal one interesting fact about the topic. "
                "It should be under 150 characters and reflect your personality. Do not repeat earlier facts."
            )

        # Generate line
        line = ask_chatgpt(prompt, temperature=0.7, max_tokens=200)

        # Save the new line if not duplicate
        if line in previous_lines:
            print("[DEBUG] Skipping insert: Line already used recently.")
        else:
            try:
                supabase.table("lines").insert({
                    "topic": topic,
                    "line": line
                }).execute()
                print("[DEBUG] Inserted new line.")
            except Exception as insert_err:
                print("[ERROR] Failed to insert line:", insert_err)

        return jsonify({"line": line})
    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"error": "Failed to generate line"}), 500