import os
from redis.asyncio import Redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

async def get_redis_client() -> Redis:
    return redis_client

