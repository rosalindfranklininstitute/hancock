import redis
from hancock import app

revoked_store = redis.StrictRedis(host=app.config['HANCOCK_REDIS_HOST'], port=6379, db=0,
                                  decode_responses=True)

