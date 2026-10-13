import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    PORT = int(os.getenv("PORT", 5001))

    # MongoDB (DB2)
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DB_NAME = os.getenv("DB_NAME", "quiz_db")

    # Secret shared with the main server - only the main server can call this service
    INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "")

    # Simulates a long quiz processing (in seconds)
    PROCESSING_DELAY_SECONDS = int(os.getenv("PROCESSING_DELAY_SECONDS", 10))

    # Email
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")
    EMAIL_FROM = os.getenv("EMAIL_FROM") or os.getenv("EMAIL_USER")
