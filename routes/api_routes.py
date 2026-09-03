from flask import Blueprint, request, jsonify
from services.prompt_service import PromptService
from db import Database

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/generate", methods=["POST"])
def generate_single():
    """
    Step 1 & Step 5: Single POST Endpoint
    Accepts: {"userInput": "How much should I score in each subject to pass CA final?"}
    Returns: {"response": "..."}
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON body is required"}), 400

        user_input = data.get("userInput")
        prompt_id = data.get("promptId")

        # Process the prompt
        result = PromptService.process_single(user_input, prompt_id)
        return jsonify(result), 200

    except ValueError as val_err:
        return jsonify({"error": str(val_err)}), 400
    except Exception as err:
        return jsonify({"error": "Internal server error", "details": str(err)}), 500


@api_bp.route("/generate/batch", methods=["POST"])
def generate_batch():
    """
    Step 6: Batch POST Endpoint (Asynchronous)
    Accepts: {"inputs": ["Question 1", "Question 2", "Question 3"]}
    Returns: {"responses": ["Answer 1", "Answer 2", "Answer 3"]}
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON body is required"}), 400

        # Support 'inputs' (or 'userInputs')
        user_inputs = data.get("inputs") or data.get("userInputs")
        prompt_id = data.get("promptId")

        # Process the batch
        result = PromptService.process_batch(user_inputs, prompt_id)
        return jsonify(result), 200

    except ValueError as val_err:
        return jsonify({"error": str(val_err)}), 400
    except Exception as err:
        return jsonify({"error": "Internal server error", "details": str(err)}), 500


@api_bp.route("/prompts", methods=["GET"])
def get_prompts():
    """Returns all prompt templates stored in MongoDB."""
    try:
        col = Database.get_prompts_collection()
        prompts = list(col.find({}, {"_id": 1, "template": 1}))
        return jsonify({"prompts": prompts}), 200
    except Exception as err:
        return jsonify({"error": str(err)}), 500


@api_bp.route("/history", methods=["GET"])
def get_history():
    """Returns recent request/response logs from the history collection."""
    try:
        limit = int(request.args.get("limit", 10))
        col = Database.get_history_collection()
        records = list(col.find().sort("timestamp", -1).limit(limit))

        # Convert ObjectId and datetime to strings for clean JSON
        for item in records:
            item["_id"] = str(item["_id"])
            if "timestamp" in item:
                item["timestamp"] = item["timestamp"].isoformat()

        return jsonify({"count": len(records), "history": records}), 200
    except Exception as err:
        return jsonify({"error": str(err)}), 500


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify database and app status."""
    db_status = Database.ping()
    return jsonify({
        "status": "healthy",
        "database": db_status
    }), 200
