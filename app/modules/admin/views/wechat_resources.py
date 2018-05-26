import json

import os
import uuid

from app import db
from app.models import SchoolScenery
from .. import admin
from flask_login import login_required
from flask import render_template, request


@admin.route('/school_scenery')
@login_required
def school_scenery():
    page = request.args.get('page', 1, type=int)
    pagination = SchoolScenery.query.order_by(SchoolScenery.create_time.desc()).paginate(page, per_page=18,
                                                                                         error_out=False)
    scenery = pagination.items
    return render_template('wechat_resources/school_scenery.html', scenery=scenery, pagination=pagination)


@admin.route('/delete_school_scenery')
@login_required
def delete_school_scenery():
    try:
        scenery = SchoolScenery.query.filter_by(id=request.args.get('id')).first()
        db.session.delete(scenery)
        db.session.commit()
        os.remove('app/static/images/school_scenery/' + scenery.img_url)
        return json.dumps({'code': 1})
    except Exception as e:
        return json.dumps({'code': -1})


@admin.route('/upload_school_scenery', methods=["POST"])
@login_required
def upload_school_scenery():
    path = os.path.abspath(os.path.join(os.getcwd(), './app/static/images/school_scenery'))
    if not os.path.exists(path):
        os.makedirs(path)
    try:
        file = request.files["file"]
        file_name = str(uuid.uuid1()) + "." + file.filename.split(".")[-1:][0]
        file.save(path + "/" + file_name)
        scenery = SchoolScenery(img_url=file_name, description=file.filename)
        scenery.id = str(uuid.uuid1())
        db.session.add(scenery)
        return json.dumps({"code": 1})
    except:
        return json.dumps({"code": -1})
