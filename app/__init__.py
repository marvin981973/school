from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    config_name = 'dev'
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    from app.modules.public import public
    from app.modules.dynamic import dynamic
    from app.modules.teacher import teacher
    from app.modules.student import student
    from app.modules.library import library
    from app.modules.lostandfound import lostandfound
    app.register_blueprint(public, url_prefix='')
    app.register_blueprint(dynamic, url_prefix='/dynamic')
    app.register_blueprint(teacher, url_prefix='/teacher')
    app.register_blueprint(student, url_prefix='/student')
    app.register_blueprint(library, url_prefix='/library')
    app.register_blueprint(lostandfound, url_prefix='/lostandfound')
    return app


def create_app_for_db():
    app = Flask(__name__)
    config_name = 'dev'
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    return app
