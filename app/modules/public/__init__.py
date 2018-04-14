from flask import Blueprint

public = Blueprint('public', __name__)

from app.modules.public import views

