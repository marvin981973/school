from flask import Blueprint

webscrapy = Blueprint('webscrapy', __name__)

from app.modules.webscrapy import views
