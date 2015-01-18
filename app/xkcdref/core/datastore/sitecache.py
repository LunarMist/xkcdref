import zlib

import redis
import simplejson

REDIS_CLAZZ = 'site_xkcdref'


class SiteCache(object):
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
        self.r = redis.StrictRedis(host=self.host, port=self.port, db=self.db)

    def _get(self, clazz, name, decompress=False):
        if not clazz or not name:
            return None

        key = clazz + '|' + name
        v = self.r.get(key)
        if decompress and v:
            v = zlib.decompress(v)
        return v

    def _set(self, clazz, name, value, compress=False):
        if not clazz or not name:
            return None

        key = clazz + '|' + name
        if compress and value:
            value = zlib.compress(value)
        return self.r.set(key, value)

    def get(self, name):
        """
        Fetch a value from the cache.
        :param name: The name of the value to fetch.
        :return: A string representation of the value being fetched.
        """
        return self._get(REDIS_CLAZZ, name)

    def set(self, name, value):
        """
        Sets a value in the cache.
        :param name: The name.
        :param value: The value to set.
        """
        return self._set(REDIS_CLAZZ, name, value)

    def get_json(self, name, decompress=True):
        v = self._get(REDIS_CLAZZ, name, decompress=decompress)
        return v if not v else simplejson.loads(v)

    def set_json(self, name, value, compress=True):
        if value is not None:
            return self._set(REDIS_CLAZZ, name, simplejson.dumps(value), compress=compress)
        return None
