from datetime import timedelta
from functools import lru_cache
import pickle
from time import time

from flask import url_for
from redis import Redis, StrictRedis
from redis.sentinel import Sentinel

__all__ = [

    # Classes
    'RedisCache',
    'MemoryCache',

    # Functions
    'caching_url_for'
]


class BaseCache:
    """
    A base class from which other cache backends should be derived, the base
    class defines the common interface all cache backends must implement.

    This manhattan caches are a replacement for those provided by
    `werkzeug.contrib.cache` previously. We don't aim to support as many
    caching backends initially (just `SimpleCache` and `RedisCache`) and we
    don't guarentee they are 100% compatible, however, our aim is to make them
    easy to use as replacements.
    """

    def __init__(
        self,
        default_timeout=300,
        pickle_protocol=pickle.HIGHEST_PROTOCOL
    ):

        # The default expiry time for a key added to the cache (0 indicates
        # that a key will never expire.
        if isinstance(default_timeout, timedelta):
            default_timeout = int(default_timeout.total_seconds())

        self.default_timeout = default_timeout

        # The protocol used when pickling objects for storage in the cache
        self._pickle_protocol = pickle_protocol

    def _normalize_timeout(self, timeout):
        """
        Return the timeout if provided or the default timeout for values if
        not.
        """
        if isinstance(timeout, timedelta):
            timeout = int(timeout.total_seconds())

        return self.default_timeout if timeout is None else timeout

    def add(self, key, value, timeout=None):
        raise NotImplemented()

    def clear(self):
        raise NotImplemented()

    def dec(self, key, delta=1):
        value = (self.get(key) or 0) - delta
        return value if self.set(key, value) else None

    def delete(key):
        raise NotImplemented()

    def delete_many(self, *keys):
        return all(self.delete(key) for key in keys)

    def get(self, key):
        raise NotImplemented()

    def get_dict(self, *keys):
        return dict(zip(keys, self.get_many(*keys)))

    def get_many(self, *keys):
        return [self.get(k) for k in keys]

    def has(self, key):
        raise NotImplemented()

    def inc(self, key, delta=1):
        value = (self.get(key) or 0) + delta
        return value if self.set(key, value) else None

    def set(self, key, value, timeout=None):
        raise NotImplemented()

    def set_many(self, mapping, timeout=None):
        result = True
        for key, value in mapping.items():
            if not self.set(key, value, timeout):
                result = False
        return result


class MemoryCache(BaseCache):
    """
    A cache that uses memory as the backend. This cache replaces `SimpleCache`
    and is provided for local development on single process environments.
    """

    def __init__(self, threshold=500, default_timeout=300):
        super().__init__(default_timeout=default_timeout)

        # The maximum number of entries supported by the cache, the cache will
        # automatically be culled when the threshold is exceeded.
        self._threshold = threshold

        # The memory cache
        self._cache = {}

    def _normalize_timeout(self, timeout):
        timeout = super()._normalize_timeout(timeout)
        return timeout if timeout == 0 else time() + timeout

    def _prune(self):
        """
        Prune the cache ensuring it is within it's threshold, expired keys are
        removed first followed by the oldest keys if required.
        """

        # Remove expired items
        now = time()
        for key, item in list(self._cache.items()):
            expires, value = item
            if expires != 0 and expires <= now:
                self._cache.pop(key, None)

        # Remove oldest items (if required)
        while len(self._cache) > self._threshold:
            self._cache.pop(self._cache.keys()[0])

    def add(self, key, value, timeout=None):
        if self.has(key):
            return False

        self._cache.setdefault(
            key,
            (
                self._normalize_timeout(timeout),
                pickle.dumps(value, self._pickle_protocol)
            )
        )
        self._prune()

        return True

    def clear(self):
        self._cache.clear()
        return True

    def delete(self, key):
        return self._cache.pop(key, None) is not None

    def get(self, key):
        try:
            expires, value = self._cache[key]
            if expires == 0 or expires > time():
                return pickle.loads(value)

        except (KeyError, pickle.PickleError):
            return None

    def has(self, key):
        try:
            expires, value = self._cache[key]
            return expires == 0 or expires > time()

        except KeyError:
            return False

    def set(self, key, value, timeout=None):
        self._cache[key] = (
            self._normalize_timeout(timeout),
            pickle.dumps(value, self._pickle_protocol)
        )
        self._prune()

        return True


class RedisCache(BaseCache):
    """
    A cache that uses Redis as the backend (with support for sentinel).
    """

    def __init__(
        self,
        host='localhost',
        port=6379,
        password=None,
        db=0,
        sentinel_master=None,
        sentinels=None,
        default_timeout=300,
        key_prefix='',
        **kwargs
    ):
        super().__init__(default_timeout=default_timeout)

        # A prefix that will be applied to all keys stored in the cache
        self._key_prefix = key_prefix

        # Setup the redis client
        if isinstance(host, str) or sentinels:

            if sentinels:
                sentinel = Sentinel(
                    sentinels,
                    db=db,
                    password=password,
                    **kwargs
                )
                self._client = sentinel.master_for(sentinel_master)

            else:
                self._client = redis = StrictRedis(
                    host=host,
                    port=port,
                    db=db,
                    password=password,
                    **kwargs
                )

        else:
            self._client = host

    def _normalize_timeout(self, timeout):
        timeout = super()._normalize_timeout(timeout)
        return -1 if timeout == 0 else timeout

    def _prefix(self, key):
        """Return a prefixed version of the given key"""
        return f'{self._key_prefix}{key}'

    def add(self, key, value, timeout=None):
        if self._client.setnx(self._prefix(key), self.dump_object(value)):

            timeout = self._normalize_timeout(timeout)
            if timeout == -1:
                return self._client.expire(self._prefix(key), timeout)

            return True

        return False

    def dump_object(self, value):
        """Deserialize an object for the Redis cache"""
        if isinstance(value, int):
            return str(value).encode('ascii')
        return b'!' + pickle.dumps(value)

    def load_object(self, value):
        """Deserialize an object from the Redis cache"""

        if value is None:
            return None

        if value.startswith(b'!'):
            try:
                return pickle.loads(value[1:])
            except pickle.PickleError:
                return None

        try:
            return int(value)
        except ValueError:
            return None

    def get(self, key):
        return self.load_object(self._client.get(self._prefix(key)))

    def get_many(self, *keys):
        if self._key_prefix:
            keys = [self._prefix(k) for k in keys]
        return [self.load_object(v) for v in self._client.mget(keys)]

    def set(self, key, value, timeout=None):
        timeout = self._normalize_timeout(timeout)
        if timeout == -1:
            return self._client.set(
                self._prefix(key),
                self.dump_object(value)
            )

        return self._client.setex(
            self._prefix(key),
            timeout,
            self.dump_object(value)
        )

    def set_many(self, mapping, timeout=None):
        timeout = self._normalize_timeout(timeout)

        # Use transaction=False to batch without calling redis MULTI
        # which is not supported by twemproxy
        pipe = self._client.pipeline(transaction=False)

        for key, value in mapping.items():

            dump = self.dump_object(value)

            if timeout == -1:
                pipe.set(self._prefix(key), self.dump_object(value))

            else:
                pipe.setex(
                    self._prefix(key),
                    timeout,
                    self.dump_object(value)
                )

        return pipe.execute()

    def delete(self, key):
        return self._client.delete(self._prefix(key))

    def delete_many(self, *keys):
        if keys:
            if self._key_prefix:
                keys = [self._prefix(k) for k in keys]
            return self._client.delete(*keys)

    def has(self, key):
        return self._client.exists(self._prefix(key))

    def clear(self):
        if self._key_prefix:
            keys = self._client.keys(f'{self._key_prefix}*')
            if keys:
                return self._client.delete(*keys)
        return self._client.flushdb()

    def inc(self, key, delta=1):
        return self._client.incr(self._prefix(key), delta)

    def dec(self, key, delta=1):
        return self._client.decr(self._prefix(key), delta)


@lru_cache(maxsize=2560)
def caching_url_for(endpoint, **values):
    """A version of `url_for` that caches the output"""
    return url_for(endpoint, **values)
