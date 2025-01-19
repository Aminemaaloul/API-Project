from flask import Blueprint, jsonify, request
from app.extensions  import db
from app.utils import calculate_compensation, admin_required
from marshmallow import ValidationError
from app.schemas import ClaimSchema
from app.models import Flight, Claim

claim_api = Blueprint('claim_api', __name__)

@claim_api.route("/api/claims/status", methods=['GET'])
def check_claim_status():
    """
    Check the status of a claim made by a passenger.
    """
    # Get query parameters
    claim_id = request.args.get('claim_id')
    passenger_name = request.args.get('passenger_name')
    flight_number = request.args.get('flight_number')

    # Validate input
    if not (claim_id or (passenger_name and flight_number)):
        return jsonify({"message": "Either claim_id or passenger_name and flight_number are required"}), 400

    # Query the database for the claim
    if claim_id:
        claim = Claim.query.get(claim_id)
    else:
        # Trim whitespace and ignore case for passenger_name and flight_number
        passenger_name = passenger_name.strip().lower()  # Remove leading/trailing spaces and convert to lowercase
        flight_number = flight_number.strip().lower()  # Remove leading/trailing spaces and convert to lowercase
        claim = Claim.query.filter(
            db.func.lower(Claim.passenger_name) == passenger_name,
            db.func.lower(Claim.flight_number) == flight_number
        ).first()

    if not claim:
        return jsonify({"message": "Claim not found"}), 404

    # Return the claim status and details
    return jsonify({
        "claim_id": claim.id,
        "passenger_name": claim.passenger_name,
        "flight_number": claim.flight_number,
        "status": claim.status,
        "claim_amount": claim.claim_amount,
        "created_at": claim.created_at.isoformat() if claim.created_at else None,
        "updated_at": claim.updated_at.isoformat() if claim.updated_at else None
    })
@claim_api.route("/api/claims", methods=['POST'])
def submit_claim():
    """
    Submit a new claim for flight delay compensation.
    :return: JSON response with claim submission result.
    """
    data = request.get_json()

    try:
        claim_data = ClaimSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    flight_number = claim_data.get('flight_number')
    flight = Flight.query.filter_by(flight_number=flight_number).first()
    if not flight:
        return jsonify({"message": "Flight not found"}), 404

    # Create a new claim with status "Pending"
    new_claim = Claim(
        passenger_name=claim_data['passenger_name'],
        flight_number=flight_number,
        claim_amount=0,  # Default value, will be updated later
        status="Pending"
    )
    db.session.add(new_claim)
    db.session.commit()

    return jsonify({
        "message": "Claim submitted successfully",
        "claim_id": new_claim.id,
        "status": new_claim.status
    })


@claim_api.route("/compensation-rules", methods=['GET'])
def get_compensation_rules():
    """
    View the rules for flight delay compensation based on the duration.
    :return: JSON response with compensation rules.
    """
    rules = [
        {"min_delay": 120, "max_delay": 180, "compensation": "100 TND"},  # 2–3 hours
        {"min_delay": 180, "max_delay": 240, "compensation": "200 TND"},  # 3–4 hours
        {"min_delay": 240, "compensation": "300 TND"}  # More than 4 hours
    ]
    return jsonify(rules)

@claim_api.route("/admin/claims", methods=['GET'])
@admin_required
def get_all_claims():
    """
    Get a list of all claims (Admin Only).
    :return: JSON response with all claims.
    """
    claims = Claim.query.all()
    
    result = []
    for claim in claims:
        flight = Flight.query.filter_by(flight_number=claim.flight_number).first()
        result.append({
            "claim_id": claim.id,
            "passenger_name": claim.passenger_name,
            "flight_number": flight.flight_number if flight else "Unknown",
            "claim_amount": claim.claim_amount,
            "status": claim.status,
            "created_at": claim.created_at,
            "updated_at": claim.updated_at
        })
    
    return jsonify(result)
    
@claim_api.route("/admin/claims/compensation/<int:claim_id>", methods=['GET'])
@admin_required  # Ensure only admins can access this endpoint
def calculate_claim_compensation(claim_id):
    """
    Calculate eligible compensation for a claim and update its status.
    :param claim_id: The ID of the claim to process.
    :return: JSON response with compensation details and updated status.
    """
    claim = Claim.query.get(claim_id)
    if not claim:
        return jsonify({"message": "Claim not found"}), 404

    flight = Flight.query.filter_by(flight_number=claim.flight_number).first()
    if not flight:
        return jsonify({"message": "Flight not found"}), 404

    # Calculate compensation based on departure delay
    compensation = calculate_compensation(flight.departure_delay)

    # Update the claim status and compensation amount
    if compensation > 0:
        claim.status = "Approved"
    else:
        claim.status = "Denied"
    claim.claim_amount = compensation

    # Commit the changes to the database
    db.session.commit()

    return jsonify({
        "claim_id": claim.id,
        "flight_number": claim.flight_number,
        "delay": flight.departure_delay,
        "eligible_compensation": f"{compensation} TND",
        "status": claim.status
    })
    
@claim_api.route("/admin/claims/<int:claim_id>", methods=['GET'])
@admin_required
def get_claim_details(claim_id):
    """
    Get detailed information about a specific claim by ID.
    :param claim_id: The ID of the claim to fetch details for.
    :return: JSON response with claim details.
    """
    claim = Claim.query.get(claim_id)

    if not claim:
        return jsonify({"message": "Claim not found"}), 404

    flight = Flight.query.filter_by(flight_number=claim.flight_number).first()
    return jsonify({
        "claim_id": claim.id,
        "passenger_name": claim.passenger_name,
        "flight_number": flight.flight_number if flight else "Unknown",
        "claim_amount": claim.claim_amount,
        "status": claim.status,
        "created_at": claim.created_at,
        "updated_at": claim.updated_at
    })