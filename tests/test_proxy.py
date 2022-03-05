import os
import json
import time
import yaml
import redis
import datetime
import requests
import unittest

with open(os.getenv('CONFIGS'), "r") as file:
    proxy_configs = yaml.load(file, Loader=yaml.FullLoader)
    REDIS_URL = proxy_configs["redis_url"]

# REDIS_URL = 'redis://backing-redis:6379'
# REDIS_URL = 'redis://localhost:6379'
redis = redis.from_url(REDIS_URL)
print(f"Created proxy.")

redis.hmset("1", {"user": "bob", "timestamp": datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%d %H:%M:%S.%f")})
redis.hmset("2", {"user": "alice", "timestamp": datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%d %H:%M:%S.%f")})
redis.hmset("3", {"user": "sam", "timestamp": datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%d %H:%M:%S.%f")})
redis.hmset("4", {"user": "jen", "timestamp": datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%d %H:%M:%S.%f")})
redis.hmset("5", {"user": "joe", "timestamp": datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%d %H:%M:%S.%f")})
redis.hmset("6", {"user": "sally", "timestamp": datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%d %H:%M:%S.%f")})


class TestCache(unittest.TestCase):
    def test_redis_backing(self):
        user = redis.hgetall("1")
        self.assertEqual(user[b"user"].decode('utf-8'), "bob")
        
    def test_get_user(self):
        expected_user = "bob"
        r = requests.get(url='http://0.0.0.0:5000/get', params={'key': '1', 'user':'bob'})
        response = json.loads(r.text)
        self.assertEqual(expected_user, response["user"])

    def test_fixed_keysize(self):
        r = requests.get(url='http://0.0.0.0:5000/cache_size')
        response = json.loads(r.text)
        self.assertEqual(response["max_cache"], 5)

    def test_lru(self):
        r = requests.get(url='http://0.0.0.0:5000/get', params={'key': '1', 'user':'bob'})
        r = requests.get(url='http://0.0.0.0:5000/get', params={'key': '2', 'user':'alice'})
        r = requests.get(url='http://0.0.0.0:5000/get', params={'key': '3', 'user':'sam'})
        r = requests.get(url='http://0.0.0.0:5000/get', params={'key': '4', 'user':'jen'})
        r = requests.get(url='http://0.0.0.0:5000/get', params={'key': '5', 'user':'joe'})
        r = requests.get(url='http://0.0.0.0:5000/get', params={'key': '6', 'user':'sally'})
        r = requests.get(url='http://0.0.0.0:5000/get', params={'key': '1', 'user':'bob'})
        response = json.loads(r.text)
        is_cache = response["from_cache"]
        self.assertEqual(response["from_cache"], "false")

    def test_expiry(self):
        time.sleep(200)
        r = requests.get(url='http://0.0.0.0:5000/get', params={'key': '2', 'user':'alice'})
        print(f"r.text: {type(r.text)}, {r.text}")
        response = json.loads(r.text)
        is_cache = response["from_cache"]
        self.assertEqual(response["from_cache"], "false")