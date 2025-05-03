import json
import os

TOPICS_FILE = "data/topics.json"

def load_topics():
    if not os.path.exists(TOPICS_FILE):
        return []
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_topics(topics):
    os.makedirs(os.path.dirname(TOPICS_FILE), exist_ok=True)
    with open(TOPICS_FILE, "w", encoding="utf-8") as f:
        json.dump(topics, f, indent=2)

