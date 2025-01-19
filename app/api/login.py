from flask import Blueprint, request, jsonify, current_app
import jwt
from datetime import datetime, timedelta
from app.models import Admin

# Define the login_api Blueprint
login_api = Blueprint('login_api', __name__)

@login_api.route("/admin/login", methods=['POST'])
def login():
    """
    Authenticate and receive a JWT token for accessing protected endpoints.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check if the admin exists in the database
    admin = Admin.query.filter_by(username=username).first()

    if admin and admin.check_password(password):
        # Generate a JWT token with a "role" claim
        token = jwt.encode({
            'username': username,
            'role': 'admin',  # Add role for role-based access control
            'exp': datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
        }, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

        return jsonify({"token": token})
    else:
        return jsonify({"message": "Invalid credentials"}), 401