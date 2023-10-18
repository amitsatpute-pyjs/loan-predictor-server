import eventlet
eventlet.monkey_patch()

from flask_socketio import SocketIO, emit
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from celery_setup import make_celery
from celery.result import AsyncResult
import redis


class Server:
    def __init__(self,name):
        self.app = Flask(name)
        self.redis = redis.Redis(host='localhost', port=6379, db=1)
        self.cors = CORS(self.app)
        self.app.config['CORS_HEADERS'] = 'Content-Type'
        self.app.config.update(
            CELERY_BROKER_URL='redis://localhost:6379/0',
            result_backend='redis://localhost:6379/0'
        )
        self.app.debug = True
        self.socketio = SocketIO(self.app, async_mode="eventlet", async_handlers=True,cors_allowed_origins="*")        
        self.celery = make_celery(self.app)


    def run(self):
        self.socketio.run(self.app)