from app import db
from datetime import datetime
from marshmallow import Schema, fields
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from dateutil import parser


class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        """Hash the password and store it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hashed password."""
        return check_password_hash(self.password_hash, password)

class Flight(db.Model):
    __tablename__ = 'flights'

    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(20), nullable=False)
    flight_date = db.Column(db.DateTime, nullable=True)
    flight_status = db.Column(db.String(20), nullable=True)
    
    # Departure details
    departure_airport = db.Column(db.String(50), nullable=True)
    departure_timezone = db.Column(db.String(50), nullable=True)
    departure_iata = db.Column(db.String(10), nullable=True)
    departure_delay = db.Column(db.Float, nullable=True, default=0.0)
    departure_scheduled = db.Column(db.DateTime, nullable=True)
    departure_actual = db.Column(db.DateTime, nullable=True)

    # Arrival details
    arrival_airport = db.Column(db.String(50), nullable=True)
    arrival_timezone = db.Column(db.String(50), nullable=True)
    arrival_iata = db.Column(db.String(10), nullable=True)
    arrival_scheduled = db.Column(db.DateTime, nullable=True)
    arrival_actual = db.Column(db.DateTime, nullable=True)
    
    # Airline details
    airline_name = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"<Flight {self.flight_number}>"

    @staticmethod
    def convert_to_datetime(datetime_str):
        """
        Convert a datetime string to a datetime object.
        Handles multiple formats, including timezone-aware strings.
        """
        if not datetime_str:
            return None  # Return None if the input is empty or None

        try:
            # Use dateutil.parser to handle multiple formats, including timezone-aware strings
            return parser.isoparse(datetime_str)
        except ValueError:
            print(f"Failed to parse datetime: {datetime_str}")
            return None

    @staticmethod
    def convert_to_datetime(datetime_str):
        """
        Convert a datetime string to a datetime object.
        Handles multiple formats, including timezone-aware strings.
        """
        if not datetime_str:
            return None  # Return None if the input is empty or None

        try:
            # Use dateutil.parser to handle multiple formats, including timezone-aware strings
            return parser.isoparse(datetime_str)
        except ValueError:
            print(f"Failed to parse datetime: {datetime_str}")
            return None

class Claim(db.Model):
    __tablename__ = 'claims'  # Explicitly set the table name to 'claims'
    id = db.Column(db.Integer, primary_key=True)
    passenger_name = db.Column(db.String(100), nullable=False)
    flight_number = db.Column(db.String(50), nullable=False)
    claim_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

# Simplified Schema for Response
class SimplifiedFlightSchema(Schema):
    id = fields.Int(dump_only=True)
    flight_number = fields.Str()
    flight_date = fields.Str()
    flight_status = fields.Str()
    departure = fields.Dict()
    arrival = fields.Dict()
    airline = fields.Dict()

    class Meta:
        fields = ("id", "flight_number", "flight_date", "flight_status", "departure", "arrival", "airline")


# Helper function to create simplified flight response
def create_simplified_flight_response(flight):
    """Helper function to create a simplified flight response."""
    return {
        "id": flight.id,
        "flight_number": flight.flight_number,
        "flight_date": flight.flight_date.isoformat() if flight.flight_date else None,
        "flight_status": flight.flight_status,
        "departure": {
            "actual": flight.departure_actual.isoformat() if flight.departure_actual else None,
            "airport": flight.departure_airport,
            "iata": flight.departure_iata,
            "delay": flight.departure_delay,  # Include the delay field
            "scheduled": flight.departure_scheduled.isoformat() if flight.departure_scheduled else None,
            "timezone": flight.departure_timezone
        },
        "arrival": {
            "actual": flight.arrival_actual.isoformat() if flight.arrival_actual else None,
            "airport": flight.arrival_airport,
            "iata": flight.arrival_iata,
            "scheduled": flight.arrival_scheduled.isoformat() if flight.arrival_scheduled else None,
            "timezone": flight.arrival_timezone
        },
        "airline": {
            "name": flight.airline_name
        }
    }