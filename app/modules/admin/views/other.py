import json

from flask import request, render_template
from flask_login import login_required, current_user

from app import db
from app.models import Notification, Feedback
from app.modules.admin import admin
from app.tools import generate_form_html


@admin.route('/other_system_notification')
@login_required
def other_system_notification():
    add_form_array = [{
        'text': '标题',
        'name': 'title'
    }, {
        'category': 'textarea',
        'text': '内容',
        'name': 'content'
    }]
    return render_template("other/system_notification.html", add_form_html=generate_form_html(add_form_array),
                           update_form_html=generate_form_html(add_form_array, mode='update'),
                           add_form_height=len(add_form_array) * 45 + 195,
                           update_form_height=len(add_form_array) * 45 + 195)


@admin.route('/load_system_notification')
@login_required
def load_system_notification():
    search_text = request.args.get('search_text', '')
    page_size = int(request.args.get('page_size', '10'))
    page_number = int(request.args.get('page_number', '1'))
    sort_name = request.args.get('sort_name', 'number')
    sort_order = request.args.get('sort_order', 'asc')

    if search_text == '':
        if sort_order == 'asc':
            pagination = Notification.query.order_by(db.asc(Notification.create_time)).paginate(page_number, page_size,
                                                                                                False)
        else:
            pagination = Notification.query.order_by(db.desc(Notification.create_time)).paginate(page_number, page_size,
                                                                                                 False)
    else:
        if sort_order == 'asc':
            pagination = Notification.query.order_by(db.asc(Notification.create_time)).paginate(page_number, page_size,
                                                                                                False)
        else:
            pagination = Notification.query.order_by(db.desc(Notification.create_time)).paginate(page_number, page_size,
                                                                                                 False)
    notifications = []
    for item in pagination.items:
        notifications.append({
            'id': item.id,
            'title': item.title,
            'content': item.content,
            'create_time': item.create_time.strftime("%Y-%m-%d") if item.create_time else None
        })
    return json.dumps({
        "total": pagination.total,
        "rows": notifications
    })


@admin.route('/other_add_system_notification', methods=['POST'])
@login_required
def other_add_system_notification():
    try:
        data = json.loads(request.data.decode())
        db.session.add(Notification(title=data["title"], content=data["content"]))
        db.session.commit()
        return json.dumps({'code': 1, 'msg': '新增成功'})
    except:
        return json.dumps({'code': -1, 'msg': '新增失败'})


@admin.route('/other_delete_system_notification', methods=['POST'])
@login_required
def other_delete_system_notification():
    try:
        data = json.loads(request.data.decode())
        for notification in data['ids']:
            db.session.delete(Notification.query.filter_by(id=notification).first())
        db.session.commit()
        return json.dumps({'code': 1})
    except:
        return json.dumps({'code': -1})


@admin.route('/other_edit_system_notification', methods=['POST'])
@login_required
def other_edit_system_notification():
    try:
        data = json.loads(request.data.decode())
        notification = Notification.query.filter_by(id=data["id"]).first()
        notification.title = data["title"]
        notification.content = data["content"]
        db.session.commit()
        return json.dumps({'code': 1, 'msg': '修改成功'})
    except Exception as e:
        return json.dumps({'code': -1, 'msg': '修改失败'})


@admin.route('/other_feedback')
@login_required
def other_feedback():
    return render_template("other/feedback.html")


@admin.route('/load_feedback')
@login_required
def load_feedback():
    search_text = request.args.get('search_text', '')
    page_size = int(request.args.get('page_size', '10'))
    page_number = int(request.args.get('page_number', '1'))
    sort_name = request.args.get('sort_name', 'number')
    sort_order = request.args.get('sort_order', 'asc')

    if search_text == '':
        if sort_order == 'asc':
            pagination = Feedback.query.order_by(db.asc(Feedback.create_time)).paginate(page_number, page_size,
                                                                                        False)
        else:
            pagination = Feedback.query.order_by(db.desc(Feedback.create_time)).paginate(page_number, page_size,
                                                                                         False)
    else:
        if sort_order == 'asc':
            pagination = Feedback.query.order_by(db.asc(Feedback.create_time)).paginate(page_number, page_size,
                                                                                        False)
        else:
            pagination = Feedback.query.order_by(db.desc(Feedback.create_time)).paginate(page_number, page_size,
                                                                                         False)
    feedback = []
    for item in pagination.items:
        feedback.append({
            'id': item.id,
            'user_id': item.user_id,
            'user_name': item.user_name,
            'content': item.content,
            'create_time': item.create_time.strftime("%Y-%m-%d") if item.create_time else None
        })
    return json.dumps({
        "total": pagination.total,
        "rows": feedback
    })
