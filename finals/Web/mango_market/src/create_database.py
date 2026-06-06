from pymongo import MongoClient
from urllib.parse import quote_plus

print("Creating Database!")

username = "ROOT"
password = "X5y<5X*`tW1%"

uri = f"mongodb://{quote_plus(username)}:{quote_plus(password)}@localhost:27017/admin"
client = MongoClient(uri)


db = client["main"]

logins = db["logins"]
products = db["products"]

admin_cred = {
    "username": "johnmango",
    "password_hash": "9f18e89040a074b867edccc126f80501", # pass: mango7
    "role": "admin",
}

logins.insert_one(admin_cred)
print(list(logins.find({})))