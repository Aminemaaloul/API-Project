# app/schemas.py
from marshmallow import Schema, fields

class ClaimSchema(Schema):
    passenger_name = fields.Str(required=True)
    flight_number = fields.Str(required=True)  # Flight number instead of flight_id
    claim_amount = fields.Float()
    status = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

