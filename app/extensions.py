from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_caching import Cache

# Initialize extensions
db = SQLAlchemy()
ma = Marshmallow()
cache = Cache()