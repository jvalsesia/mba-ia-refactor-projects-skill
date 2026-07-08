"""Layer 6 — Composition root / entry point.

The application factory wires config, the database extension, the route
blueprints, and the centralized error handler together. Nothing self-
instantiates global connections at import time — everything is constructed here.
"""
from flask import Flask
from flask_cors import CORS

from config import settings
from database import db
import models  # noqa: F401 — register models before create_all()
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from routes.category_routes import category_bp
from routes.report_routes import report_bp
from middleware.error_handler import register_error_handlers
from utils.timeutils import now_utc


def create_app(config=settings):
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SECRET_KEY'] = config.SECRET_KEY

    CORS(app)
    db.init_app(app)

    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(report_bp)

    register_error_handlers(app)

    @app.route('/health')
    def health():
        return {'status': 'ok', 'timestamp': str(now_utc())}

    @app.route('/')
    def index():
        return {'message': 'Task Manager API', 'version': '1.0'}

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=settings.DEBUG, host=settings.HOST, port=settings.PORT)
