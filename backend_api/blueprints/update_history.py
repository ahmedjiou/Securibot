from flask import Blueprint, request, jsonify
from firebase_admin import auth
from . import convo_bp

from db.db_config import db
from datetime import datetime

@convo_bp.route("/api/currentConvo/", methods=["POST", "OPTIONS"])
def update_conversation():

    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
        return response, 200
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
        provided_title = conv_data.get("title", None)

        # Validate messages
        if not isinstance(messages, list) or len(messages) == 0:
            return jsonify({"error": f"'messages' must be a non-empty list for conversationId {conv_id}"}), 400

        for msg in messages:
            if not all(k in msg for k in ["sender", "text", "timestamp"]):
                return jsonify({"error": f"Incomplete message: {msg}"}), 400
            if msg["sender"] not in ["user", "bot"]:
                return jsonify({"error": f"Invalid sender in message: {msg}"}), 400

        # Generate title if not provided
        if not provided_title:
            # Find first user message
            first_user_msg = next((m for m in messages if m["sender"] == "user"), None)
            if first_user_msg:
                words = first_user_msg["text"].split()
                auto_title = " ".join(words[:3]) if words else "Untitled"
            else:
                auto_title = "Untitled"

            title = auto_title
        else:
            title = provided_title

        # Add title and lastUpdated timestamp to conv_data
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
