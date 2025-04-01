from pymongo import MongoClient

MONGO_URI = "mongodb+srv://admin:Forex123.@forex-cluster.sasxvc3.mongodb.net/?retryWrites=true&w=majority&appName=forex-cluster"

client = MongoClient(MONGO_URI)
db = client["forex_db"]  # Name der Datenbank
