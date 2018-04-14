from flask import Blueprint

teacher=Blueprint('teacher',__name__)

from app.modules.teacher import views