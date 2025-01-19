from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

def create_swagger_spec(app):
    """
    Dynamically generates the OpenAPI specification for the Flask app.
    """
    # Create an APISpec instance
    spec = APISpec(
        title="Flight Delay Compensation API",
        version="1.0.0",
        openapi_version="3.0.0",
        plugins=[FlaskPlugin(), MarshmallowPlugin()],
    )

    # Add security scheme (JWT)
    spec.components.security_scheme(
        "JWT",
        {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    )

    # Add schemas (request/response models)
    spec.components.schema("ClaimRequest", {
        "type": "object",
        "properties": {
            "passenger_name": {"type": "string"},
            "flight_number": {"type": "string"}
        },
        "required": ["passenger_name", "flight_number"]
    })

    spec.components.schema("ClaimResponse", {
        "type": "object",
        "properties": {
            "message": {"type": "string"},
            "claim_id": {"type": "integer"},
            "status": {"type": "string"}
        }
    })

    spec.components.schema("CompensationRule", {
        "type": "object",
        "properties": {
            "min_delay": {"type": "integer"},
            "max_delay": {"type": "integer"},
            "compensation": {"type": "string"}
        }
    })

    spec.components.schema("ClaimDetails", {
        "type": "object",
        "properties": {
            "claim_id": {"type": "integer"},
            "passenger_name": {"type": "string"},
            "flight_number": {"type": "string"},
            "claim_amount": {"type": "number"},
            "status": {"type": "string"},
            "created_at": {"type": "string", "format": "date-time"},
            "updated_at": {"type": "string", "format": "date-time"}
        }
    })

    spec.components.schema("CompensationDetails", {
        "type": "object",
        "properties": {
            "claim_id": {"type": "integer"},
            "flight_number": {"type": "string"},
            "delay": {"type": "number"},
            "eligible_compensation": {"type": "string"},
            "status": {"type": "string"}
        }
    })

    spec.components.schema("Flight", {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "flight_number": {"type": "string"},
            "flight_date": {"type": "string", "format": "date-time"},
            "flight_status": {"type": "string"},
            "departure": {
                "type": "object",
                "properties": {
                    "airport": {"type": "string"},
                    "timezone": {"type": "string"},
                    "iata": {"type": "string"},
                    "delay": {"type": "number"},
                    "scheduled": {"type": "string", "format": "date-time"},
                    "actual": {"type": "string", "format": "date-time"}
                }
            },
            "arrival": {
                "type": "object",
                "properties": {
                    "airport": {"type": "string"},
                    "timezone": {"type": "string"},
                    "iata": {"type": "string"},
                    "scheduled": {"type": "string", "format": "date-time"},
                    "actual": {"type": "string", "format": "date-time"}
                }
            },
            "airline": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                }
            }
        }
    })

    spec.components.schema("FlightRequest", {
        "type": "object",
        "properties": {
            "flight_number": {"type": "string"},
            "flight_date": {"type": "string", "format": "date-time"},
            "flight_status": {"type": "string"},
            "departure": {
                "type": "object",
                "properties": {
                    "airport": {"type": "string"},
                    "timezone": {"type": "string"},
                    "iata": {"type": "string"},
                    "delay": {"type": "number"},
                    "scheduled": {"type": "string", "format": "date-time"},
                    "actual": {"type": "string", "format": "date-time"}
                }
            },
            "arrival": {
                "type": "object",
                "properties": {
                    "airport": {"type": "string"},
                    "timezone": {"type": "string"},
                    "iata": {"type": "string"},
                    "scheduled": {"type": "string", "format": "date-time"},
                    "actual": {"type": "string", "format": "date-time"}
                }
            },
            "airline": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                }
            }
        }
    })

    spec.components.schema("FlightResponse", {
        "type": "object",
        "properties": {
            "message": {"type": "string"},
            "flight_number": {"type": "string"}
        }
    })

    spec.components.schema("LoginRequest", {
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "password": {"type": "string"}
        },
        "required": ["username", "password"]
    })

    spec.components.schema("LoginResponse", {
        "type": "object",
        "properties": {
            "token": {"type": "string"}
        }
    })

    # Add paths (endpoints)
    with app.test_request_context():
        # Add /api/claims endpoint
        spec.path(
            view=app.view_functions['claim_api.submit_claim'],
            operations={
                "post": {
                    "summary": "Submit a new claim",
                    "description": "Submit a new claim for flight delay compensation.",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ClaimRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Claim submitted successfully.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ClaimResponse"}
                                }
                            }
                        },
                        "400": {"description": "Invalid input data."},
                        "404": {"description": "Flight not found."}
                    }
                }
            }
        )

        # Add /compensation-rules endpoint
        spec.path(
            view=app.view_functions['claim_api.get_compensation_rules'],
            operations={
                "get": {
                    "summary": "Get compensation rules",
                    "description": "View the rules for flight delay compensation based on the duration.",
                    "responses": {
                        "200": {
                            "description": "Compensation rules returned successfully.",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/CompensationRule"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        )
        spec.path(
    view=app.view_functions['flight_api.delete_flight'],
    operations={
        "delete": {
            "summary": "Delete a flight",
            "description": "Delete a specific flight by flight_number. Requires admin access.",
            "parameters": [
                {
                    "name": "flight_number",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"}
                }
            ],
            "responses": {
                "200": {
                    "description": "Flight deleted successfully.",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/FlightResponse"}
                        }
                    }
                },
                "401": {
                    "description": "Unauthorized. Invalid or missing token."
                },
                "403": {
                    "description": "Forbidden. Admin access required."
                },
                "404": {
                    "description": "Flight not found."
                }
            },
            "security": [{"JWT": []}]  # <-- Add security requirement
        }
    }
)

        # Add /admin/claims endpoint
        spec.path(
            view=app.view_functions['claim_api.get_all_claims'],
            operations={
                "get": {
                    "summary": "Get all claims (Admin Only)",
                    "description": "Get a list of all claims. Requires admin access.",
                    "responses": {
                        "200": {
                            "description": "List of claims returned successfully.",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/ClaimDetails"}
                                    }
                                }
                            }
                        }
                    },
                    "security": [{"JWT": []}]
                }
            }
        )
        spec.path(
    view=app.view_functions['claim_api.check_claim_status'],
    operations={
        "get": {
            "summary": "Check the status of a claim",
            "description": "Retrieve the status of a claim using either the claim ID or the passenger name and flight number.",
            "parameters": [
                {
                    "name": "claim_id",
                    "in": "query",
                    "description": "The unique ID of the claim.",
                    "required": False,
                    "schema": {"type": "integer"}
                },
                {
                    "name": "passenger_name",
                    "in": "query",
                    "description": "The name of the passenger.",
                    "required": False,
                    "schema": {"type": "string"}
                },
                {
                    "name": "flight_number",
                    "in": "query",
                    "description": "The flight number associated with the claim.",
                    "required": False,
                    "schema": {"type": "string"}
                }
            ],
            "responses": {
                "200": {
                    "description": "Claim details retrieved successfully.",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "claim_id": {"type": "integer", "example": 1},
                                    "passenger_name": {"type": "string", "example": "Becher Zribi"},
                                    "flight_number": {"type": "string", "example": "TU343"},
                                    "status": {"type": "string", "example": "Approved"},
                                    "claim_amount": {"type": "number", "format": "float", "example": 100.0},
                                    "created_at": {"type": "string", "format": "date-time", "example": "2025-01-19T04:26:48"},
                                    "updated_at": {"type": "string", "format": "date-time", "example": "2025-01-19T05:14:43"}
                                }
                            }
                        }
                    }
                },
                "400": {
                    "description": "Invalid input. Either claim_id or passenger_name and flight_number are required.",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "message": {"type": "string", "example": "Either claim_id or passenger_name and flight_number are required"}
                                }
                            }
                        }
                    }
                },
                "404": {
                    "description": "Claim not found.",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "message": {"type": "string", "example": "Claim not found"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)

        # Add /api/claims/compensation/{claim_id} endpoint
        spec.path(
            view=app.view_functions['claim_api.calculate_claim_compensation'],
            operations={
                "get": {
                    "summary": "Calculate claim compensation",
                    "description": "Calculate eligible compensation for a claim and update its status. Requires admin access.",
                    "parameters": [
                        {
                            "name": "claim_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Compensation calculated successfully.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CompensationDetails"}
                                }
                            }
                        },
                        "404": {"description": "Claim or flight not found."}
                    },
                    "security": [{"JWT": []}]
                }
            }
        )

        # Add /api/claims/{claim_id} endpoint
        spec.path(
            view=app.view_functions['claim_api.get_claim_details'],
            operations={
                "get": {
                    "summary": "Get claim details",
                    "description": "Get detailed information about a specific claim by ID. Requires admin access.",
                    "parameters": [
                        {
                            "name": "claim_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Claim details returned successfully.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ClaimDetails"}
                                }
                            }
                        },
                        "404": {"description": "Claim not found."}
                    },
                    "security": [{"JWT": []}]
                }
            }
        )

        # Add /api/flights endpoint
        spec.path(
            view=app.view_functions['flight_api.get_flights'],
            operations={
                "get": {
                    "summary": "Get all flights",
                    "description": "Fetch all flights departing from Tunis-Carthage Airport (TUN).",
                    "responses": {
                        "200": {
                            "description": "List of flights returned successfully.",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Flight"}
                                    }
                                }
                            }
                        },
                        "404": {"description": "No flight data available."},
                        "500": {"description": "Failed to fetch flight data."}
                    }
                }
            }
        )
        
        # Add /api/flights (POST) endpoint
        spec.path(
    view=app.view_functions['flight_api.add_flight'],
    operations={
        "post": {
            "summary": "Add a new flight",
            "description": "Add a new flight to the database. Requires admin access.",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/FlightRequest"}
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "Flight added successfully.",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/FlightResponse"}
                        }
                    }
                },
                "400": {
                    "description": "Invalid input data."
                },
                "401": {
                    "description": "Unauthorized. Invalid or missing token."
                },
                "403": {
                    "description": "Forbidden. Admin access required."
                }
            },
            "security": [{"JWT": []}]  # <-- Add security requirement
        }
    }
)
        
        # Add /api/flights/{flight_number} (GET) endpoint
        spec.path(
        view=app.view_functions['flight_api.get_flight_details'],
        operations={
        "get": {
            "summary": "Get flight details",
            "description": "Fetch the details of a specific flight by its flight number.",
            "parameters": [
                {
                    "name": "flight_number",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                    "description": "The flight number of the flight to retrieve."
                }
            ],
            "responses": {
                "200": {
                    "description": "Flight details retrieved successfully.",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/FlightResponse"}
                        }
                    }
                },
                "404": {
                    "description": "Flight not found."
                }
            }
        }
    }
)

        

        # Add /api/flights/{flight_number} (PUT) endpoint
        # Add /api/flights/{flight_number} (PUT) endpoint
        spec.path(
    view=app.view_functions['flight_api.update_flight'],
    operations={
        "put": {
            "summary": "Update flight details",
            "description": "Update details of a specific flight by flight_number. Requires admin access.",
            "parameters": [
                {
                    "name": "flight_number",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"}
                }
            ],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/FlightRequest"}
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "Flight updated successfully.",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/FlightResponse"}
                        }
                    }
                },
                "401": {
                    "description": "Unauthorized. Invalid or missing token."
                },
                "403": {
                    "description": "Forbidden. Admin access required."
                },
                "404": {
                    "description": "Flight not found."
                }
            },
            "security": [{"JWT": []}]  # <-- Add security requirement
        }
    }
)
        spec.path(
    view=app.view_functions['flight_api.get_flight_details'],
    operations={
        "get": {
            "summary": "Get flight details",
            "description": "Fetch the details of a specific flight by its flight number.",
            "parameters": [
                {
                    "name": "flight_number",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                    "description": "The flight number of the flight to retrieve."
                }
            ],
            "responses": {
                "200": {
                    "description": "Flight details retrieved successfully.",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/FlightResponse"}
                        }
                    }
                },
                "404": {
                    "description": "Flight not found."
                }
            }
        }
    }
)

        # Add /api/login endpoint
        spec.path(
            view=app.view_functions['login_api.login'],
            operations={
                "post": {
                    "summary": "Authenticate and receive a JWT token",
                    "description": "Authenticate and receive a JWT token for accessing protected endpoints.",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/LoginRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Authentication successful.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/LoginResponse"}
                                }
                            }
                        },
                        "401": {"description": "Invalid credentials."}
                    }
                }
            }
        )

    return spec