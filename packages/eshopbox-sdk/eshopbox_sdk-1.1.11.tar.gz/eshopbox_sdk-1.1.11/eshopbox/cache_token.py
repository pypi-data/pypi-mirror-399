import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)


class TokenCache:
    def __init__(self):
        self.redis_client = r
        self.expires_in = 2592000  # 30 days

    def get_token(self, key):
        return self.redis_client.get(key) or None

    def set_token(self, key, token):
        self.redis_client.setex(key, self.expires_in, token)
