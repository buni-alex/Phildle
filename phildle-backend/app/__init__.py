from flask import Flask
from flask_cors import CORS
from .db import init_db

def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)

    app.config.from_object("app.config.Config")
    init_db(app)

    from .routes import phildle, philosophers, history
    app.register_blueprint(phildle.bp)
    app.register_blueprint(philosophers.bp)
    app.register_blueprint(history.bp)

    return app