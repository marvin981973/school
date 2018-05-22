from flask import Blueprint

admin = Blueprint('admin', __name__)

from app.modules.admin import views, errors
