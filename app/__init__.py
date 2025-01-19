from flask import Flask, jsonify
from dotenv import load_dotenv
from .extensions import db, ma, cache  # Import extensions from extensions.py
from flask_migrate import Migrate  # Import Migrate for database migrations
from flask_swagger_ui import get_swaggerui_blueprint  # Import Swagger UI
from .swagger import create_swagger_spec  # Import the create_swagger_spec function

# Load environment variables from .env file
load_dotenv()

# Initialize Migrate
migrate = Migrate()

def create_app():
    """
    Application factory function to create and configure the Flask app.
    """
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    cache.init_app(app)
    migrate.init_app(app, db)

    # Configure Swagger UI
    SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI
    API_URL = '/swagger.json'  # URL for serving the OpenAPI specification

    # Create Swagger UI blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Flight Delay Compensation API",  # Name of your API
            'layout': "BaseLayout",  # Layout for Swagger UI
            'deepLinking': True,  # Enable deep linking for tags and operations
            'displayOperationId': True,  # Display operation IDs
        }
    )

    # Register Blueprints
    from .api.flight import flight_api
    from .api.claim import claim_api
    from .api.docs import docs_api
    from .api.login import login_api  # Import the login_api Blueprint

    # Register Swagger UI blueprint
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Register API blueprints
    app.register_blueprint(flight_api)
    app.register_blueprint(claim_api)
    app.register_blueprint(docs_api)
    app.register_blueprint(login_api)  # Register the login_api Blueprint

    # Add a route to serve the OpenAPI specification (swagger.json)
    @app.route('/swagger.json')
    def serve_swagger_json():
        """
        Serve the OpenAPI specification (swagger.json).
        """
        spec = create_swagger_spec(app)  # Generate the OpenAPI specification dynamically
        return jsonify(spec.to_dict())  # Return the spec as JSON

    return app