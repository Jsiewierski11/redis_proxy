import json
import redis
import datetime
import requests
from waitress import serve
from flask import Flask, jsonify

from typing import OrderedDict

app = Flask(__name__)
app.config.from_object(__name__)

# app.config['SESSION_REDIS'] = redis.from_url(REDIS_URL)

# cache = redis.from_url(REDIS_URL)
# pubsub = cache.pubsub()

class LRU(OrderedDict):
    def __init__(self, maxsize=5, expiry=60, *args, **kwds):
        self.maxsize = maxsize
        self.expiry = expiry
        super().__init__(*args, **kwds)
        
    def __getitem__(self, __k):
        user = super().__getitem__(__k)
        self.move_to_end(__k)
        return user

    def __setitem__(self, __k, v):
        super().__setitem__(__k, v)
        if len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]

class Proxy:
    def __init__(self, host, port, redis_url, cache_size, expiry) -> None:
        self.host = host
        self.port = port
        self.expiry = expiry
        self.redis = redis.from_url(redis_url)
        self.cache = LRU(cache_size, expiry)
        # self.timestamp = datetime.datetime.utcnow()

    def run(self, flask, mode='dev'):
        print(f"Flask type: {type(flask)}")
        print(f"Flask Client running on {self.host}:{self.port}")
        if mode == 'prod':
            serve(app=flask, host=self.host, port=self.port)
        else:
            flask.run(host=self.host,
                      port=self.port,
                      debug=True,
                      threaded=True)