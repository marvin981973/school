from flask import Blueprint

admin = Blueprint('admin', __name__)

from app.modules.admin import view, errors
from app.modules.admin.views import user, wechat_resources, other
