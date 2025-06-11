from . import convo_bp
from flask import request, jsonify
from firebase_admin import auth
from db.db_config import db
from datetime import datetime

"""
    Fetches the full conversation details for a given conversation ID.

    This endpoint retrieves the complete conversation document from the Firestore database 
    for a specified conversation ID, after validating the provided Firebase JWT.

    **Request Headers:**
    - `Authorization`: A Bearer token for authentication.

    **Request Body:**
    - `conversationId`: The ID of the conversation to fetch.

    **Returns:**
    - A JSON object with the full conversation details and a 200 status code on success.
    - An error message and a 400, 401, or 404 status code on failure.
"""
@convo_bp.route("/api/getFullConvo/", methods=["POST", "OPTIONS"])
def post_full_conversation():
    # Extract and validate JWT
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
        return response, 200

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Authorization header missing or malformed"}), 401

    id_token = auth_header.split("Bearer ")[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
    except Exception as e:
        return jsonify({"error": "Invalid or expired token", "details": str(e)}), 401

    # Parse JSON payload to get conversationId
    try:
        payload = request.get_json()
        conversation_id = payload.get("conversationId")
        if not conversation_id:
            return jsonify({"error": "Missing conversationId in request body"}), 400
    except Exception as e:
        return jsonify({"error": "Invalid JSON payload", "details": str(e)}), 400

    # Fetch full conversation document from Firestore
    conv_doc = db.collection("conversations").document(uid).collection("user_conversations").document(conversation_id).get()
    print(conv_doc)
    if not conv_doc.exists:
        return jsonify({"error": "Conversation not found"}), 404

    return jsonify(conv_doc.to_dict()), 200
