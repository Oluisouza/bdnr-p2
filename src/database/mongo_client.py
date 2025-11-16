import os 
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")

client = AsyncIOMotorClient(MONGO_URL)
db: AsyncIOMotorDatabase = client.transflow_db

async def get_mongo_db() -> AsyncIOMotorDatabase:
    return db

