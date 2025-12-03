from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()  # .env 로드

def create_app():
    app = Flask(__name__)

    from .routes.index import index_bp
    from .routes.high1 import high1_bp
    from .routes.high2 import high2_bp
    from .routes.high3 import high3_bp

    app.register_blueprint(index_bp)
    app.register_blueprint(high1_bp)
    app.register_blueprint(high2_bp)
    app.register_blueprint(high3_bp)

    return app
