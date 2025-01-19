from functools import wraps
from flask import request, jsonify, current_app
import jwt

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({"message": "Authorization header is missing"}), 401

        # Check if the header starts with "Bearer"
        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "Invalid token format. Use 'Bearer <token>'"}), 401

        # Extract the token (remove "Bearer " prefix)
        token = auth_header.split(" ")[1]

        try:
            # Decode the token
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])

            # Check if the user has the 'admin' role
            if data.get('role') != 'admin':
                return jsonify({"message": "Admin access required"}), 403

        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"message": f"An error occurred: {str(e)}"}), 500

        return f(*args, **kwargs)

    return decorated
def calculate_compensation(delay):
    """
    Calculate compensation based on the delay duration.
    :param delay: The delay duration in minutes.
    :return: Compensation amount as a numeric value.
    """
    if delay < 120:
        return 0  # No compensation for delays under 2 hours
    elif 120 <= delay < 180:
        return 100  # 2–3 hours
    elif 180 <= delay < 240:
        return 200  # 3–4 hours
    else:
        return 300  # More than 4 hours
    