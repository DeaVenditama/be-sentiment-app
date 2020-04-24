from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')
    cors = CORS(app)

    db.init_app(app)

    with app.app_context():
        from .Routes import HashtagRoutes
        from .Routes import TweetRoutes
        return app