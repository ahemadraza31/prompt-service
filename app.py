from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from db import Database
from routes.api_routes import api_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    with app.app_context():
        Database.seed_default_prompts()

    app.register_blueprint(api_bp)

    @app.route("/", methods=["GET"])
    def home():
        return jsonify({
            "message": "Intucate LLM Prompt Service is running!",
            "endpoints": {
                "single_post": "POST /api/generate",
                "batch_post": "POST /api/generate/batch",
                "history": "GET /api/history",
                "prompts": "GET /api/prompts",
                "health": "GET /api/health"
            }
        }), 200

    return app


if __name__ == "__main__":
    app = create_app()
    print(f"Starting server on http://localhost:{Config.PORT}...")
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
