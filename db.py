from pymongo import MongoClient
from config import MONGO_URL

client = MongoClient(MONGO_URL)
db = client["Alex"]

users = db["users"]
movies = db["movies"]
likes = db["likes"]
requests = db["requests"]
downloads = db["downloads"]
