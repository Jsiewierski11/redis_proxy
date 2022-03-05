from dataclasses import dataclass
import re
import os
import json
from sqlite3 import Timestamp
import yaml
import redis
import requests
import datetime
from flask import Flask, jsonify, request

from proxy import Proxy, app

# TODO: Make this configurable from startup
# REDIS_URL = 'redis://backing-redis:6379'
# print(f"Setting redis to url of {REDIS_URL}")

if __name__ == "__main__":
    proxy = None

    @app.route('/get/', methods=['GET'])
    def get_user():
        try:
            print("Get request called")
            print(f"Request received: {request}")
            # payload = json.loads(request.data.decode('utf-8'))
            payload = request.args.to_dict()
            print(f"payload: {payload}")
            # time_now = datetime.datetime.utcnow()
            if payload["key"] in proxy.cache:
                user_timestamp = payload["key"]
                user = proxy.redis.hgetall(payload["key"])
                timechange = datetime.datetime.strptime(user[b"timestamp"].decode('utf-8'), '%Y-%m-%d %H:%M:%S.%f') + datetime.timedelta(seconds=proxy.expiry)
                if timechange < datetime.datetime.fromtimestamp(proxy.expiry):
                    print(f"User in cache")
                    proxy.redis.hset(payload["key"], datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%d %H:%M:%S.%f"))
                    return {"user": proxy.cache[payload["key"]], "from_cache": "true"}
                else:
                    print(f"user not in cache, get from backing redis.")
                    user_map = proxy.redis.hgetall(payload["key"])
                    print(f"user_map: {type(user_map)}, {user_map}")
                    
                    user = user_map[b"user"].decode('utf-8')
                    print(f"user: {type(user)}, {user}")
                    proxy.cache[payload["key"]] = user
                    return {"user": user, "from_cache": "false"}
            else:
                print(f"user not in cache, get from backing redis.")
                user_map = proxy.redis.hgetall(payload["key"])
                print(f"user_map: {type(user_map)}, {user_map}")
                
                user = user_map[b"user"].decode('utf-8')
                print(f"user: {type(user)}, {user}")
                proxy.cache[payload["key"]] = user

                print(f"user retrieved from backing redis - {user_map}")
                return {"user": user, "from_cache": "false"}
        except Exception as e:
            print(f"Something went wrong - {e}")
            return f"Error - {e}\n"

    @app.route('/cache_size', methods=['GET'])
    def get_cache_size():
        with open(os.getenv('CONFIGS'), "r") as file:
            proxy_configs = yaml.load(file, Loader=yaml.FullLoader)
            return {"cache_size": len(proxy.cache), "max_cache": proxy_configs['cache_size']}

    @app.route('/set', methods=['POST'])
    def set_user():
        try:
            print("Set user called")
            payload = json.loads(request.data.decode('utf-8'))
            print(f"payload from request: {payload}")
            tstamp = datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%d %H:%M:%S.%f")
            user_map = {"user": payload["user"], "timestamp": tstamp}
            print(f"tstamp: {tstamp}")
            proxy.redis.hmset(payload["key"], user_map)
            # proxy.redis.hset(payload["key"], tstamp)
            # proxy.redis.hset(payload["key"], payload["user"])
            # proxy.redis.set(payload["key"], payload["user"])
            return "User " + payload["key"] + " stored in redis.\n"
        except Exception as e:
            print(f"Exception in set_user - {e}")

    with open(os.getenv('CONFIGS'), "r") as file:
        proxy_configs = yaml.load(file, Loader=yaml.FullLoader)
        proxy = Proxy(host=proxy_configs['host'], 
                      port=proxy_configs['port'], 
                      redis_url=proxy_configs['redis_url'], 
                      expiry=proxy_configs['expiry_time'],
                      cache_size=proxy_configs['cache_size'])

        proxy.run(app, mode=proxy_configs['flask_mode'])