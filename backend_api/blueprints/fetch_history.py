from flask import Blueprint, request, jsonify
from firebase_admin import auth
from . import convo_bp
from db.db_config import db
from datetime import datetime

# Pour fetcher l'historique des conversations
@convo_bp.route("/api/getUserConvos/", methods=["POST", "OPTIONS"])
def post_conversation_list():
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
        print("Options request received")
        return response, 200

    print("Fetching conversation list...")
    # Get the Firebase JWT token
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Authorization header missing or malformed"}), 401

    id_token = auth_header.split("Bearer ")[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
    except Exception as e:
        return jsonify({"error": "Invalid or expired token", "details": str(e)}), 401

    # Fetch user's ConvoHistory field from users/{uid}
    user_doc = db.collection("users").document(uid).get()
    if not user_doc.exists:
        return jsonify({"conversations": []})

    convo_ids = user_doc.to_dict().get("ConvoHistory", [])
    print(convo_ids)
    results = []

    # For each conversation ID, fetch title from conversations/{uid}/user_conversations/{id}
    for cid in convo_ids:
        conv_doc = db.collection("conversations").document(uid).collection("user_conversations").document(cid).get()
        if conv_doc.exists:
            data = conv_doc.to_dict()
            results.append({
                "conversationId": cid,
                "title": data.get("title", "Untitled")
            })

    return jsonify({"conversations": results}), 200