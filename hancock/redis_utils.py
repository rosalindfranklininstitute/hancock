import redis

revoked_store = redis.StrictRedis(host=current_app.config['HANCOCK_REDIS_HOST'], port=6379, db=0,
                                  decode_responses=True)


class RedisManager:

    def __init__(self, app=None, db=None, **kwargs):
        self.app = app
        if app is not None:
            self.init_app(app, db, **kwargs)

    def init_app(self, app, db, **kwargs):
        self.db = db

        app.config.setdefault('xxx', xxx)

        # Bind Flask-Foo to app
        app.manager = self