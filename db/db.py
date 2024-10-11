from motor.motor_asyncio import AsyncIOMotorClient
from config.config import MONGO_URI
from datetime import datetime

client = AsyncIOMotorClient(MONGO_URI)
db = client["telegram_stats"]
messages_collection = db["messages"]
users_collection = db["users"]

async def add_message(user_id: int, message_id: int, date):
    await messages_collection.insert_one({
        "user_id": user_id,
        "message_id": message_id,
        "date": date
    })

async def update_user_message_count(user_id: int):
    user_stat = await users_collection.find_one({"user_id": user_id})
    if user_stat:
        await users_collection.update_one(
            {"user_id": user_id},
            {"$inc": {"message_count": 1}}
        )
    else:
        await users_collection.insert_one({
            "user_id": user_id,
            "message_count": 1,
            "joined_at": datetime.now()
        })
        
async def add_new_user(user_id: int):
    user_stat = await users_collection.find_one({"user_id": user_id})
    
    if not user_stat:
        await users_collection.insert_one({
            "user_id": user_id,
            "message_count": 0,
            "joined_at": datetime.now()
        })
        print(f"New user {user_id} added to the database.")
    else:
        print(f"User {user_id} already exists in the database.")
