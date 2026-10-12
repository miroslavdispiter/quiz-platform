from flask import Flask
from app.Database.db import db
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.Extensions.bcrypt import bcrypt
from app.config import Config
from app.Extensions.socketio_ext import socketio
from app.WebAPI.controllers.AuthController import auth_bp
from app.WebAPI.controllers.UserController import user_bp

jwt = JWTManager()

def create_app():
    from dotenv import load_dotenv
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    db.init_app(app)

    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')

    with app.app_context():
        db.create_all()

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/users")

    @app.get("/")
    def home():
        return {"status": "ok", "service": "drs server"}

    return app

