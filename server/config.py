import redis
import os

try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv(".env"))
except ImportError:
    print("dotenv not installed, skipping...")


REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "root")

REDIS_CLIENT = redis.Redis(
    host="localhost", port=6379, password=REDIS_PASSWORD, decode_responses=True
)


DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
