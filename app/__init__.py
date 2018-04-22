from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func,select
from app.config import config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    config_name = 'dev'
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    from app.modules.public import public
    from app.modules.webscrapy import webscrapy
    from app.modules.teacher import teacher
    from app.modules.student import student
    from app.modules.library import library
    from app.modules.upload import upload
    app.register_blueprint(public, url_prefix='')
    app.register_blueprint(webscrapy, url_prefix='/web')
    app.register_blueprint(teacher, url_prefix='/teacher')
    app.register_blueprint(student, url_prefix='/student')
    app.register_blueprint(library, url_prefix='/library')
    app.register_blueprint(upload, url_prefix='/upload')
    return app
