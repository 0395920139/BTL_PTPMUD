import redis
from gatco_sqlalchemy import SQLAlchemy
from application.server import app

db = SQLAlchemy()

redis_db = redis.StrictRedis(host=app.config.get('SESSION_REDIS_ADDR'),\
                             port=app.config.get('SESSION_REDIS_PORT'),\
                             db=app.config.get('SESSION_REDIS_DB'),\
                             password=None)

notify_redisdb = redis.StrictRedis(host="0.0.0.0", port=6379, db=13, password=None)
socket_redisdb = redis.StrictRedis(host="127.0.0.1", port=6379, db=11, password=None)

def init_database(app):
    db.init_app(app)
