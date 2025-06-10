from flask import Blueprint, request, jsonify
from firebase_admin import auth
from backend_api.blueprints import convo_bp
from db.db_config import db
from datetime import datetime




"""
Updates a user's conversation history.

This endpoint accepts a list of conversations, validates the data, and updates the user's conversation history in the Firebase database.

**Request Body:**
A JSON list of conversations, where each conversation item contains:
  - `conversationId`: A unique identifier for the conversation
  - `conversation`: An object containing conversation data, including:
    - `messages`: A list of message objects, each containing:
      - `sender`: The sender of the message (either "user" or "bot")
      - `text`: The text content of the message
      - `timestamp`: The timestamp of the message

**Authentication:**
This endpoint requires a valid Bearer token in the `Authorization` header.

**Returns:**
A JSON response with a status message, and a 200 status code on success, or an error response with a 400 or 401 status code on failure.
"""
@convo_bp.route("/api/currentConvo/", methods=["POST"])
def update_conversation():
    # Step 1: Get and verify Firebase token
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Authorization header missing or malformed"}), 401

    id_token = auth_header.split("Bearer ")[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
    except Exception as e:
        return jsonify({"error": "Invalid or expired token", "details": str(e)}), 401

    try:
        # Step 2: Parse JSON list of conversation objects
        conv_list = request.get_json()
        if not isinstance(conv_list, list):
            raise ValueError("Expected a list of conversations")
    except Exception as e:
        return jsonify({"error": "Invalid JSON payload", "details": str(e)}), 400

    conv_ids = []

    for item in conv_list:
        conv_id = item.get("conversationId")
        conv_data = item.get("conversation")

        if not conv_id or not isinstance(conv_data, dict):
            return jsonify({"error": f"Invalid item format: {item}"}), 400

        messages = conv_data.get("messages", [])
        title = conv_data.get("title", "Untitled Conversation")

        # Validate messages
        if not isinstance(messages, list):
            return jsonify({"error": f"'messages' must be a list for conversationId {conv_id}"}), 400
        for msg in messages:
            if not all(k in msg for k in ["sender", "text", "timestamp"]):
                return jsonify({"error": f"Incomplete message: {msg}"}), 400
            if msg["sender"] not in ["user", "bot"]:
                return jsonify({"error": f"Invalid sender in message: {msg}"}), 400

        # Add timestamp metadata
        conv_data["title"] = title
        conv_data["lastUpdated"] = datetime.utcnow().isoformat()

        # Save the conversation to Firestore
        db.collection("conversations").document(uid).collection("user_conversations").document(conv_id).set(conv_data, merge=True)
        conv_ids.append(conv_id)

    # Step 3: Update user's ConvoHistory list
    user_doc_ref = db.collection("users").document(uid)
    user_doc = user_doc_ref.get()

    if user_doc.exists:
        existing_ids = user_doc.to_dict().get("ConvoHistory", [])
    else:
        existing_ids = []

    # Combine without duplicates
    updated_history = list(set(existing_ids + conv_ids))
    user_doc_ref.set({"ConvoHistory": updated_history}, merge=True)

    return jsonify({"status": "Conversations saved", "conversations": conv_ids}), 200
