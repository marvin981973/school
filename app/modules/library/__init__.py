from flask import Blueprint

library = Blueprint('library', __name__)

from app.modules.library import views
