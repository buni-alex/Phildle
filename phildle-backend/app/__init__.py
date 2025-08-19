import os
from flask import Flask, send_file, send_from_directory
from flask_cors import CORS
from .db import init_db

def create_app():
    static_path = os.path.join(os.path.dirname(__file__), "../static")
    app = Flask(__name__, static_folder=static_path)
    CORS(app, supports_credentials=True)

    app.config.from_object("app.config.Config") 
    init_db(app)

    from .routes import phildle, philosophers, history 
    app.register_blueprint(phildle.bp) 
    app.register_blueprint(philosophers.bp) 
    app.register_blueprint(history.bp)

    ENV = os.getenv("APP_ENV", "dev")

    if ENV == "prod":
        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def catch_all(path):
            if path.startswith("api"):
                return {"error": "API route not found"}, 404

            file_path = os.path.join(app.static_folder, path)
            if path != "" and os.path.exists(file_path):
                return send_from_directory(app.static_folder, path)

            return send_file(os.path.join(app.static_folder, "index.html"))
    elif ENV == "dev":
        # in dev we don't mount catch-all
        # Vue dev server handles the frontend
        @app.route("/")
        def index():
            return {"message": "Backend is running in API-only mode"}

    return app