from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models import Flight, create_simplified_flight_response
from app.flight_service import fetch_tunis_flights 
from app.utils import admin_required# Import your fetcher

flight_api = Blueprint('flight_api', __name__)

@flight_api.route('/api/flights', methods=['GET'])
def get_flights():
    """
    Get a list of flights.
    :return: JSON response with flight details.
    """
    # Fetch fresh flight data from the external API and save to DB
    flights = fetch_tunis_flights(skip_saving=False)  # Ensure fresh data is saved in the DB

    # If the fetch was unsuccessful, return an error message
    if flights is None:
        return jsonify({"error": "Failed to fetch flight data"}), 500

    # Query the database to get all flights
    flights_db = Flight.query.all()

    # Check if no flights exist in the database
    if not flights_db:
        return jsonify({"message": "No flight data available."}), 404

    # Simplify the response data
    result = [create_simplified_flight_response(flight) for flight in flights_db]
    return jsonify(result)


@flight_api.route('/admin/flights', methods=['POST'])
@admin_required  # Apply the JWT authentication decorator
def add_flight():
    """
    Add a new flight.
    :return: JSON response with the new flight details.
    """
    data = request.get_json()

    # Validate incoming data
    if not data or 'flight_number' not in data or 'flight_status' not in data:
        return jsonify({"message": "Invalid or missing data"}), 400

    # Check for duplicate flight
    existing_flight = Flight.query.filter_by(flight_number=data['flight_number']).first()
    if existing_flight:
        return jsonify({"message": "Flight with this number already exists"}), 400

    # Convert datetime fields
    try:
        flight_date = Flight.convert_to_datetime(data.get('flight_date'))
        departure_scheduled = Flight.convert_to_datetime(data.get('departure', {}).get('scheduled'))
        departure_actual = Flight.convert_to_datetime(data.get('departure', {}).get('actual'))
        arrival_scheduled = Flight.convert_to_datetime(data.get('arrival', {}).get('scheduled'))
        arrival_actual = Flight.convert_to_datetime(data.get('arrival', {}).get('actual'))
    except Exception as e:
        return jsonify({"message": "Invalid datetime format"}), 400

    # Validate required fields
    if not all([flight_date, departure_scheduled, arrival_scheduled]):
        return jsonify({"message": "Missing or invalid datetime fields"}), 400

    # Map the incoming API data to the Flight model fields
    new_flight = Flight(
        flight_number=data['flight_number'],  # Flight number from external API
        flight_date=flight_date,  # Flight date from external API
        flight_status=data['flight_status'],  # Flight status (e.g., cancelled) from external API
        departure_airport=data['departure']['airport'],  # Departure airport from external API
        departure_timezone=data['departure']['timezone'],  # Departure timezone from external API
        departure_iata=data['departure']['iata'],  # Departure IATA code from external API
        departure_delay=data['departure'].get('delay', 0.0),  # Departure delay from external API
        departure_scheduled=departure_scheduled,  # Scheduled departure from external API
        departure_actual=departure_actual,  # Actual departure from external API
        arrival_airport=data['arrival']['airport'],  # Arrival airport from external API
        arrival_timezone=data['arrival']['timezone'],  # Arrival timezone from external API
        arrival_iata=data['arrival']['iata'],  # Arrival IATA code from external API
        arrival_scheduled=arrival_scheduled,  # Scheduled arrival from external API
        arrival_actual=arrival_actual,  # Actual arrival from external API
        airline_name=data['airline']['name']  # Airline name from external API
    )

    # Add and commit to database
    try:
        db.session.add(new_flight)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Database error:", str(e))
        return jsonify({"message": "Failed to add flight to database"}), 500

    return jsonify({
        "message": "Flight added successfully",
        "flight_number": new_flight.flight_number
    })

@flight_api.route('/api/flights/<string:flight_number>', methods=['GET'])
def get_flight_details(flight_number):
    """
    Get details of a specific flight by flight_number.
    :param flight_number: The flight_number of the flight to fetch details for.
    :return: JSON response with flight details.
    """
    flight = Flight.query.filter_by(flight_number=flight_number).first()

    if not flight:
        return jsonify({"message": "Flight not found"}), 404

    # Simplify the response data
    simplified_flight = {
        "flight_number": flight.flight_number,
        "flight_date": flight.flight_date.isoformat() if flight.flight_date else None,
        "flight_status": flight.flight_status,
        "departure": {
            "airport": flight.departure_airport,
            "timezone": flight.departure_timezone,
            "iata": flight.departure_iata,
            "delay": flight.departure_delay,
            "scheduled": flight.departure_scheduled.isoformat() if flight.departure_scheduled else None,
            "actual": flight.departure_actual.isoformat() if flight.departure_actual else None
        },
        "arrival": {
            "airport": flight.arrival_airport,
            "timezone": flight.arrival_timezone,
            "iata": flight.arrival_iata,
            "scheduled": flight.arrival_scheduled.isoformat() if flight.arrival_scheduled else None,
            "actual": flight.arrival_actual.isoformat() if flight.arrival_actual else None
        },
        "airline": {
            "name": flight.airline_name
        }
    }
    return jsonify(simplified_flight)


@flight_api.route('/admin/flights/<string:flight_number>', methods=['PUT'])
@admin_required  # Apply the JWT authentication decorator
def update_flight(flight_number):
    """
    Update details of a specific flight by flight_number.
    :param flight_number: The flight_number of the flight to update.
    :return: JSON response with the updated flight details.
    """
    data = request.get_json()
    flight = Flight.query.filter_by(flight_number=flight_number).first()

    if not flight:
        return jsonify({"message": "Flight not found"}), 404

    # Log incoming data for debugging
    print("Incoming data:", data)

    # Update the flight details with the incoming data
    if 'flight_number' in data:
        flight.flight_number = data['flight_number']
    if 'flight_date' in data:
        flight.flight_date = Flight.convert_to_datetime(data['flight_date'])
    if 'flight_status' in data:
        flight.flight_status = data['flight_status']

    # Update departure details
    if 'departure' in data:
        departure = data['departure']
        if 'airport' in departure:
            flight.departure_airport = departure['airport']
        if 'timezone' in departure:
            flight.departure_timezone = departure['timezone']
        if 'iata' in departure:
            flight.departure_iata = departure['iata']
        if 'delay' in departure:
            flight.departure_delay = departure['delay']
        if 'scheduled' in departure:
            flight.departure_scheduled = Flight.convert_to_datetime(departure['scheduled'])
        if 'actual' in departure:
            flight.departure_actual = Flight.convert_to_datetime(departure['actual'])

    # Update arrival details
    if 'arrival' in data:
        arrival = data['arrival']
        if 'airport' in arrival:
            flight.arrival_airport = arrival['airport']
        if 'timezone' in arrival:
            flight.arrival_timezone = arrival['timezone']
        if 'iata' in arrival:
            flight.arrival_iata = arrival['iata']
        if 'scheduled' in arrival:
            flight.arrival_scheduled = Flight.convert_to_datetime(arrival['scheduled'])
        if 'actual' in arrival:
            flight.arrival_actual = Flight.convert_to_datetime(arrival['actual'])

    # Update airline details
    if 'airline' in data and 'name' in data['airline']:
        flight.airline_name = data['airline']['name']

    db.session.commit()

    return jsonify({"message": "Flight updated successfully"})

@flight_api.route('/admin/flights/<string:flight_number>', methods=['DELETE'])
@admin_required  # Apply the JWT authentication decorator
def delete_flight(flight_number):
    """
    Delete a specific flight by flight_number.
    :param flight_number: The flight_number of the flight to delete.
    :return: JSON response with the deletion result.
    """
    flight = Flight.query.filter_by(flight_number=flight_number).first()

    if not flight:
        return jsonify({"message": "Flight not found"}), 404

    # Delete the flight from the database
    db.session.delete(flight)
    db.session.commit()

    return jsonify({"message": "Flight deleted successfully"})
