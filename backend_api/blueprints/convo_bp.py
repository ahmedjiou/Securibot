from flask import Blueprint, request, jsonify
from firebase_admin import auth
from db.db_config import db
from datetime import datetime

convo_bp = Blueprint("convo", __name__)

