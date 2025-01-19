from flask import Blueprint, jsonify

docs_api = Blueprint('docs_api', __name__)

@docs_api.route("/api/docs", methods=['GET'])
def api_docs():
    """
    API Documentation listing all available endpoints.
    :return: JSON response with a list of available endpoints.
    """
    return jsonify({
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/flights",
                "description": "Fetch all flights departing from Tunis-Carthage Airport (TUN)."
            },
            {
                "method": "POST",
                "path": "/api/flights",
                "description": "Add a new flight to the database."
            },
            {
                "method": "GET",
                "path": "/api/flights/<string:flight_number>",
                "description": "Get details of a specific flight by flight number."
            },
            {
                "method": "PUT",
                "path": "/api/flights/<string:flight_number>",
                "description": "Update details of a specific flight by flight number."
            },
            {
                "method": "POST",
                "path": "/api/claims",
                "description": "Submit a new claim for flight delay compensation."
            },
            {
                "method": "GET",
                "path": "/api/claims/<int:claim_id>",
                "description": "Get detailed information about a specific claim by ID."
            },
            {
                "method": "GET",
                "path": "/compensation-rules",
                "description": "View the rules for flight delay compensation based on the duration."
            },
            {
                "method": "GET",
                "path": "/admin/claims",
                "description": "Get a list of all claims (Admin Only)."
            },
            {
                "method": "GET",
                "path": "/api/claims/compensation/<int:claim_id>",
                "description": "Calculate eligible compensation based on the flight number."
            },
            {
                "method": "POST",
                "path": "/api/login",
                "description": "Authenticate and receive a JWT token for accessing protected endpoints."
            }
        ]
    })