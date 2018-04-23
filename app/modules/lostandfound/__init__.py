from flask import Blueprint

lostandfound = Blueprint("lostandfound", __name__)

from app.modules.lostandfound import views
