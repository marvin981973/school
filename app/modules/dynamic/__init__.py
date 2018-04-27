from flask import Blueprint

dynamic = Blueprint('dynamic', __name__)

from app.modules.dynamic import views
