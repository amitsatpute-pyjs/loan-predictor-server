import os
import redis
from celery.result import AsyncResult
from celery_setup import make_celery
from flask_cors import CORS, cross_origin
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit

import eventlet
eventlet.monkey_patch()


class Server:
    def __init__(self, name):
        self.app = Flask(name)
        self.redis = redis.Redis(host=os.getenv("REDIS_HOST"),
                                 port=int(os.getenv("REDIS_PORT")), db=1)
        self.cors = CORS(self.app)
        self.app.config['CORS_HEADERS'] = 'Content-Type'
        self.app.config.update(
            CELERY_BROKER_URL=f'redis://{os.getenv("REDIS_HOST")}:{ os.getenv("REDIS_PORT")}/0',
            result_backend=f'redis://{os.getenv("REDIS_HOST")}:{ os.getenv("REDIS_PORT")}/0'
        )
        self.app.debug = True
        self.socketio = SocketIO(
            self.app, async_mode="eventlet", async_handlers=True, cors_allowed_origins="*")
        self.celery = make_celery(self.app)

    def run(self):
        self.socketio.run(self.app, host="0.0.0.0")
