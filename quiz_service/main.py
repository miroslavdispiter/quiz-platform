import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from WebAPI.routes import quiz_db

load_dotenv()

def create_quiz_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(quiz_db, url_prefix="/api/quizzes")

    return app

if __name__ == "__main__":
    app = create_quiz_app()
    port = int(os.getenv("SERVER_PORT", 5001))
    print(f"Quiz Service pokrenut na portu {port}")
    app.run(debug=True, port=port)