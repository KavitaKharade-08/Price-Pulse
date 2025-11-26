from flask import Blueprint, request, jsonify
from firebase_admin import auth, firestore
from firebase_config import db
import requests

auth_routes = Blueprint('auth_routes', __name__)

# REGISTER USER
@auth_routes.route('/register', methods=['POST'])
def register_user():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    try:
        # create user in firebase auth
        user = auth.create_user(email=email, password=password)

        # store user details in firestore
        db.collection("users").document(user.uid).set({
            "name": name,
            "email": email,
            "role": "normal",
            "createdAt": firestore.SERVER_TIMESTAMP
        })

        return jsonify({"status": "success", "message": "User registered successfully"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400



# LOGIN USER
@auth_routes.route('/login', methods=['POST'])
def login_user():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    # Replace with your Firebase Web API Key
    API_KEY = "AIzaSyB4KRkX6ZKoPClVhl4-y2aUPKqwgjrzElQ"

    login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(login_url, json=payload)
    result = response.json()

    if "idToken" in result:
        # On successful login, we also fetch user firestore data
        user_id = result["localId"]
        user_doc = db.collection("users").document(user_id).get()

        if user_doc.exists:
            user_data = user_doc.to_dict()
        else:
            user_data = {}

        return jsonify({
            "status": "success",
            "message": "Login successful",
            "idToken": result["idToken"],
            "refreshToken": result["refreshToken"],
            "uid": user_id,
            "user": user_data
        }), 200

    else:
        return jsonify({"status": "error", "message": result.get("error", {})}), 400
