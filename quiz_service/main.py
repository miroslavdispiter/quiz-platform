import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

def create_quiz_app():
    app = Flask(__name__)
    CORS(app)

    return app

if __name__ == "__main__":
    app = create_quiz_app()
    port = int(os.getenv("SERVER_PORT", 5001))
    print(f"Quiz Service started at port: {port}")
    app.run(debug=True, port=port)