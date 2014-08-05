import redis
import json

decode = lambda x: json.loads(x)
encode = lambda x: json.dumps(x)

class ShhState(object):

    def __init__(self):
        self.prefix = 'shh'
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)

    def prefix_key(func):
        def newfunc(self, key, *args, **kwargs):
            if self.prefix:
                newkey = "{}:{}".format(self.prefix, key)
            else:
                newkey = key
            return func(self, newkey, *args, **kwargs)
        return newfunc

    @prefix_key
    def get_or_set_to_default(self, key, default_value=None):
        value = self.get(key)
        if value is None:
            self.set(key, default_value)
        return self.get(key)

    @prefix_key
    def get(self, key, default_value=None):
        value = self.redis.get(key)
        if value:
            return decode(value)
        else:
            return default_value

    @prefix_key
    def set(self, key, value):
        self.redis.set(key, encode(value))

    @prefix_key
    def delete(self, key):
        self.redis.delete(key)
