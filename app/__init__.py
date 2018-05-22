from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import config
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

db = SQLAlchemy()
bootstrap = Bootstrap()

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = 'admin.login'


def create_app():
    app = Flask(__name__)
    config_name = 'dev'
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)

    from app.modules.public import public
    from app.modules.dynamic import dynamic
    from app.modules.teacher import teacher
    from app.modules.student import student
    from app.modules.library import library
    from app.modules.lostandfound import lostandfound
    from app.modules.admin import admin
    app.register_blueprint(public, url_prefix='')
    app.register_blueprint(dynamic, url_prefix='/dynamic')
    app.register_blueprint(teacher, url_prefix='/teacher')
    app.register_blueprint(student, url_prefix='/student')
    app.register_blueprint(library, url_prefix='/library')
    app.register_blueprint(lostandfound, url_prefix='/lostandfound')
    app.register_blueprint(admin, url_prefix='/admin')
    return app


def create_app_for_db():
    app = Flask(__name__)
    config_name = 'dev'
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    return app
