from flask import Blueprint

student = Blueprint('student', __name__)

from app.modules.student import views
