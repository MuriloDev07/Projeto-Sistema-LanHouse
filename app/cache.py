import os
import redis

REDIS_HOST = os.getenv('REDIS_HOST', 'taciana_redis')
REDIS_PORT = int(os.getenv('REDIS_POST', 6379))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=True
)