from flask import Flask
from flask_cors import CORS  # 👈 Add this
from routes.elevenlabs import elevenlabs_blueprint
from routes.chatgpt import chatgpt_blueprint
from routes.player import player_blueprint
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv("a.env")

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Enable CORS for all routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    app.register_blueprint(elevenlabs_blueprint)
    app.register_blueprint(chatgpt_blueprint)
    app.register_blueprint(player_blueprint)

    return app

# Only run if this file is executed directly
if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
