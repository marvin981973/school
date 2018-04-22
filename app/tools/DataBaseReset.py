from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import config
import json
import uuid
from datetime import datetime

app = Flask(__name__)
config_name = 'dev'
app.config.from_object(config[config_name])
config[config_name].init_app(app)

db = SQLAlchemy(app)






def reset():
    # db.drop_all()
    db.create_all()


if __name__ == '__main__':
    reset()
