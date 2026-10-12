import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class MongoDatabase:
    def __init__(self):
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.client = MongoClient(uri)
        self.db = self.client[os.getenv("DB_NAME", "quiz_db")]
    
    def get_collection(self, name):
        return self.db[name]

db_mongo = MongoDatabase()

