# slot-sorter/slot_sorter/__init__.py
from flask import Flask

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    # The in-memory store for records.
    # For a production app, this would be a database.
    app.config['RECORDS_STORE'] = []

    from . import routes
    app.register_blueprint(routes.main_bp)

    return app