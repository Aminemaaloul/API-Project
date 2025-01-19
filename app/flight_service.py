import os
import requests
from dotenv import load_dotenv
from app.models import Flight, db, create_simplified_flight_response
from datetime import datetime

# Load environment variables
load_dotenv()

def fetch_tunis_flights(skip_saving=False):
    """
    Fetch flights from Tunis-Carthage Airport (TUN).
    Optionally skip saving the results to the database.
    """
    api_key = os.getenv("AVIATIONSTACK_API_KEY")
    if not api_key:
        print("API key is missing.")
        return None

    url = f"https://api.aviationstack.com/v1/flights?access_key={api_key}&dep_iata=TUN"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx/5xx responses
        print(f"Response Status Code: {response.status_code}")  # Log status code

        # Check if response contains the expected 'data' field
        data = response.json()
        if 'data' not in data:
            print(f"Error: 'data' not found in response: {data}")
            return None

        flights_data = data['data']
        if not flights_data:
            print("No flight data found.")
            return None

        flights = []
        for flight in flights_data:
            flight_number = flight.get('flight', {}).get('iata', 'Unknown')
            flight_status = flight.get('flight_status', 'Unknown')
            flight_date = flight.get('flight_date', 'Unknown')

            # Departure details
            departure = flight.get('departure', {})
            departure_airport = departure.get('airport', 'Unknown')
            departure_timezone = departure.get('timezone', 'Unknown')
            departure_iata = departure.get('iata', 'Unknown')
            departure_delay = departure.get('delay', 0.0)  # Default to 0 if missing
            departure_scheduled = departure.get('scheduled', None)
            departure_actual = departure.get('actual', None)

            # Arrival details
            arrival = flight.get('arrival', {})
            arrival_airport = arrival.get('airport', 'Unknown')
            arrival_timezone = arrival.get('timezone', 'Unknown')
            arrival_iata = arrival.get('iata', 'Unknown')
            arrival_scheduled = arrival.get('scheduled', None)
            arrival_actual = arrival.get('actual', None)

            # Airline details
            airline = flight.get('airline', {})
            airline_name = airline.get('name', 'Unknown')

            flight_info = {
                "flight_date": flight_date,
                "flight_status": flight_status,
                "flight_number": flight_number,
                "airline_name": airline_name,
                "departure": {
                    "airport": departure_airport,
                    "timezone": departure_timezone,
                    "iata": departure_iata,
                    "delay": departure_delay,  # Ensure delay is included
                    "scheduled": departure_scheduled,
                    "actual": departure_actual,
                },
                "arrival": {
                    "airport": arrival_airport,
                    "timezone": arrival_timezone,
                    "iata": arrival_iata,
                    "scheduled": arrival_scheduled,
                    "actual": arrival_actual,
                },
            }
            flights.append(flight_info)

        if not skip_saving:
            save_flights_to_db(flights)

        # Fetch the saved flights from the database and simplify the response
        saved_flights = Flight.query.all()
        simplified_flights = [create_simplified_flight_response(flight) for flight in saved_flights]
        return simplified_flights

    except requests.exceptions.RequestException as e:
        print(f"Error fetching flight data: {e}")
        return None


def format_datetime(dt):
    """Format a datetime object to the required string format."""
    if dt:
        return dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    return None


def save_flights_to_db(flights):
    for flight_data in flights:
        # Extract and handle missing flight_number
        flight_number = flight_data.get('flight_number')
        if not flight_number:
            print(f"Missing flight_number, skipping flight: {flight_data}")
            continue  # Skip if flight_number is missing

        # Convert datetime fields
        flight_date = Flight.convert_to_datetime(flight_data.get('flight_date'))
        departure_scheduled = Flight.convert_to_datetime(flight_data.get('departure', {}).get('scheduled'))
        departure_actual = Flight.convert_to_datetime(flight_data.get('departure', {}).get('actual'))
        arrival_scheduled = Flight.convert_to_datetime(flight_data.get('arrival', {}).get('scheduled'))
        arrival_actual = Flight.convert_to_datetime(flight_data.get('arrival', {}).get('actual'))

        # If the flight already exists in the DB, skip it
        existing_flight = Flight.query.filter_by(flight_number=flight_number).first()
        if existing_flight:
            print(f"Flight {flight_number} already exists, skipping.")
            continue

        # Insert the flight into the database
        new_flight = Flight(
            flight_number=flight_number,
            flight_date=flight_date,
            flight_status=flight_data.get('flight_status', 'Unknown'),
            departure_airport=flight_data.get('departure', {}).get('airport', 'Unknown'),
            departure_timezone=flight_data.get('departure', {}).get('timezone', 'Unknown'),
            departure_iata=flight_data.get('departure', {}).get('iata', 'Unknown'),
            departure_delay=flight_data.get('departure', {}).get('delay', 0.0),  # Ensure delay is included
            departure_scheduled=departure_scheduled,
            departure_actual=departure_actual,
            arrival_airport=flight_data.get('arrival', {}).get('airport', 'Unknown'),
            arrival_timezone=flight_data.get('arrival', {}).get('timezone', 'Unknown'),
            arrival_iata=flight_data.get('arrival', {}).get('iata', 'Unknown'),
            arrival_scheduled=arrival_scheduled,
            arrival_actual=arrival_actual,
            airline_name=flight_data.get('airline', {}).get('name', 'Unknown')
        )
        
        # Add and commit to the database
        db.session.add(new_flight)
        db.session.commit()
        print(f"Flight {flight_number} added to the database.")