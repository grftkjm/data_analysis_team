from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    # static_folder와 template_folder를 명시적으로 지정합니다.
    app = Flask(__name__, 
                static_folder='static',    # app/static 폴더를 가리킴
                template_folder='templates') # app/templates 폴더를 가리킴

    from .routes.index import index_bp
    from .routes.high1 import high1_bp
    from .routes.high2 import high2_bp
    from .routes.high3 import high3_bp
    from .routes.certificates import certificates_bp

    app.register_blueprint(index_bp)
    app.register_blueprint(high1_bp)
    app.register_blueprint(high2_bp)
    app.register_blueprint(high3_bp)
    app.register_blueprint(certificates_bp)

    return app