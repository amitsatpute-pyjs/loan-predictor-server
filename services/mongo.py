import pymongo


class MongoClient:
    def __init__(self):
        self.conn = pymongo.MongoClient('mongodb://mongo:27017/')
        self.db = self.conn["loan_approval"]
