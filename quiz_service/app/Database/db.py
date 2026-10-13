from pymongo import MongoClient
from app.config import Config

# One connection to MongoDB (DB2) for the whole service.
# Every process (also the quiz processing process) gets its own connection,
# because it imports this module again.
client = MongoClient(Config.MONGO_URI, tz_aware=True)
db = client[Config.DB_NAME]

quizzes_collection = db["quizzes"]
results_collection = db["results"]
