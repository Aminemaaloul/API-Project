import os
from dotenv import load_dotenv  # Import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///flights.db'  # SQLite database for simplicity
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Caching configuration (if you need caching)
    CACHE_TYPE = "simple"  # This can be "simple", "redis", or other options based on your requirements
    CACHE_DEFAULT_TIMEOUT = 300  # Cache timeout in seconds (optional)
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

    # Debug: Print environment variables
    print("SECRET_KEY:", SECRET_KEY)
    print("JWT_SECRET_KEY:", JWT_SECRET_KEY)

    # Ensure keys are set
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY is not set in the environment variables.")
    if not JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY is not set in the environment variables.")