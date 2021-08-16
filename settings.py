__author__ = "Suyash Soni"
__email__ = "suyash.soni248@gmail.com"

import os
from flask import Flask
from flask import Flask, jsonify
from bson.json_util import ObjectId
import json

__basedir__ = os.path.abspath(os.path.dirname(__file__))

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

app = Flask(__name__)
app.json_encoder = JSONEncoder

# Ideally, there will be one config class per environment(dev, qa, uat, prod)
class __Config__(object):
    MYSQL_DB_CONFIG = {
        'URI_CONFIG': {
            'database': 'plagiarism_detection',
            'host': 'localhost',
            'username': 'root',
            'password': '',
            'port': '3306'
        },
        'MYSQL_CONNECTION_POOL_SIZE': os.environ.get('MYSQL_CONNECTION_POOL_SIZE', 5)
    }
    FIELDS_SEPARATOR = '|'
    LOGGING = {
        'LEVEL': 'INFO'
    }
    USERAUTHID = 1
    ANNOUNCEMENTID = 1
    ENTITYID = 1


app.config.from_object(__Config__)
config = app.config
config['APPLICATION_ROOT'] = __basedir__

__all__ = ["config", "app"]
