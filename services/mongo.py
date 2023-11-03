import pymongo


class MongoClient:
    def __init__(self):
        self.conn = pymongo.MongoClient('mongodb://root:password@0.0.0.0:27017/')
        self.db = self.conn["loan_approval"]
