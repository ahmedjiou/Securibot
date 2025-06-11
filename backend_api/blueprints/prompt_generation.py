# routes/mistral_prompt.py
from flask import Blueprint, request, jsonify
from firebase_admin import auth
from datetime import datetime
from utils.chatbot import generate_response

mistral_bp = Blueprint('mistral_bp', __name__)

@mistral_bp.route("/api/generate/", methods=["POST", "OPTIONS"])
def generate_prompt_for_mistral():
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
        return response, 200
    # Step 1: Verify Firebase JWT
    # Faut voir comment faire pour le guest mode si jamais 
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Authorization header missing or malformed"}), 401

    id_token = auth_header.split("Bearer ")[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
    except Exception as e:
        return jsonify({"error": "Invalid or expired token", "details": str(e)}), 401

    # Step 2: Parse the JSON payload
    try:
        data = request.get_json()
        prompt = data.get("prompt")
        context = data.get("context", [])

        

        if not prompt:
            return jsonify({"error": "Missing prompt"}), 400

        if not isinstance(context, list):
            return jsonify({"error": "Context must be a list"}), 400
    except Exception as e:
        return jsonify({"error": "Invalid JSON body", "details": str(e)}), 400

    
    # Combine the prompt and FOR NOW DONT QUERY THE MODEL JUST SHOW THE PROMPT 
    response = generate_response(prompt, context)

    print(response)
   

    return jsonify({
        "final_prompt": response,
        "status": "Prompt generated successfully"
    }), 200
