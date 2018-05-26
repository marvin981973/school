import json

from flask import request, render_template
from flask_login import login_required, current_user

from app import db
from app.models import Student, Teacher, Admin, College
from app.modules.admin import admin
from app.tools import generate_form_html, generate_select_option


@admin.route('/user_student')
@login_required
def user_student():
    form_array = [[{
        'text': '学号',
        'name': 'number'
    }, {
        'text': '姓名',
        'name': 'name'
    }], [{
        'category': 'select',
        'text': '性别',
        'name': 'sex',
        'options': [{
            'text': '男',
            'value': '1'
        }, {
            'text': '女',
            'value': '0'
        }]
    }, {
        'text': '年龄',
        'type': 'number',
        'max': '50',
        'min': '1',
        'name': 'age'
    }], {
        'text': '入学年份',
        'type': 'number',
        'name': 'entrance_year'
    }, [{
        'category': 'select',
        'text': '学院',
        'name': 'college_id',
        'options': generate_select_option(College.query.all(), 'name', 'id')
    }, {
        'category': 'select',
        'text': '班级',
        'name': 'classes_id',
        'options': [{
            'text': '1',
            'value': '1'
        }, {
            'text': '2',
            'value': '2'
        }, {
            'text': '3',
            'value': '3'
        }]
    }]]
    return render_template("user/student.html", add_form_html=generate_form_html(form_array),
                           update_form_html=generate_form_html(form_array),
                           add_form_height=len(form_array) * 45 + 125, update_form_height=len(form_array))


@admin.route('/load_student')
@login_required
def load_student():
    search_text = request.args.get('search_text', '')
    page_size = int(request.args.get('page_size', '10'))
    page_number = int(request.args.get('page_number', '1'))
    sort_name = request.args.get('sort_name', 'number')
    sort_order = request.args.get('sort_order', 'asc')

    if search_text == '':
        if sort_order == 'asc':
            pagination = Student.query.order_by(db.asc(Student.number)).paginate(page_number, page_size, False)
        else:
            pagination = Student.query.order_by(db.desc(Student.number)).paginate(page_number, page_size, False)
    else:
        if sort_order == 'asc':
            pagination = Student.query.order_by(db.asc(Student.number)).paginate(page_number, page_size, False)
        else:
            pagination = Student.query.order_by(db.desc(Student.number)).paginate(page_number, page_size, False)
    students = []
    for item in pagination.items:
        students.append({
            'number': item.number,
            'name': item.name,
            'signature': item.signature,
            'age': item.age,
            'sex': item.sex,
            'entrance_year': item.entrance_year,
            'classes_id': item.classes_id,
            'class': item.classes.name,
            'college': item.college.name,
            'college_id': item.college_id,
            'birth_day': item.birth_day.strftime("%Y-%m-%d") if item.birth_day else None,
            'head_url': item.head_url,
            'telephone': item.telephone,
            'mail': item.mail,
        })
    return json.dumps({
        "total": pagination.total,
        "rows": students
    })


@admin.route('/user_delete_student', methods=['POST'])
@login_required
def user_delete_student():
    try:
        data = json.loads(request.data.decode())
        for stu in data['number']:
            db.session.delete(Student.query.filter_by(number=stu).first())
        db.session.commit()
        return json.dumps({'code': 1})
    except:
        return json.dumps({'code': -1})


@admin.route('/user_teacher')
@login_required
def user_teacher():
    form_array = [[{
        'text': '工号',
        'name': 'number'
    }, {
        'text': '姓名',
        'name': 'name'
    }], [{
        'category': 'select',
        'text': '性别',
        'name': 'sex',
        'options': [{
            'text': '男',
            'value': '1'
        }, {
            'text': '女',
            'value': '0'
        }]
    }, {
        'text': '年龄',
        'type': 'number',
        'max': '50',
        'min': '1',
        'name': 'age'
    }], {
        'category': 'select',
        'text': '学院',
        'name': 'college',
        'options': [{
            'text': '1',
            'value': '1'
        }, {
            'text': '2',
            'value': '2'
        }, {
            'text': '3',
            'value': '3'
        }]
    }, {
        'text': 'sdsdsdsd',
        'name': 'sdsdfsdfsd'
    }]
    return render_template("user/teacher.html", add_form_html=generate_form_html(form_array),
                           update_form_html=generate_form_html(form_array),
                           add_form_height=len(form_array) * 45 + 125, update_form_height=len(form_array) * 45 + 125)


@admin.route('/load_teacher')
@login_required
def load_teacher():
    search_text = request.args.get('search_text', '')
    page_size = int(request.args.get('page_size', '10'))
    page_number = int(request.args.get('page_number', '1'))
    sort_name = request.args.get('sort_name', 'number')
    sort_order = request.args.get('sort_order', 'asc')

    if search_text == '':
        if sort_order == 'asc':
            pagination = Teacher.query.order_by(db.asc(Teacher.number)).paginate(page_number, page_size, False)
        else:
            pagination = Teacher.query.order_by(db.desc(Teacher.number)).paginate(page_number, page_size, False)
    else:
        if sort_order == 'asc':
            pagination = Teacher.query.order_by(db.asc(Teacher.number)).paginate(page_number, page_size, False)
        else:
            pagination = Teacher.query.order_by(db.desc(Teacher.number)).paginate(page_number, page_size, False)
    teachers = []
    for item in pagination.items:
        teachers.append({
            'number': item.number,
            'name': item.name,
            'signature': item.signature,
            'age': item.age,
            'sex': item.sex,
            'college': item.college.name,
            'college_id': item.college_id,
            'birth_day': item.birth_day.strftime("%Y-%m-%d") if item.birth_day else None,
            'head_url': item.head_url,
            'telephone': item.telephone,
            'mail': item.mail,
        })
    return json.dumps({
        "total": pagination.total,
        "rows": teachers
    })


@admin.route('/user_delete_teacher', methods=['POST'])
@login_required
def user_delete_teacher():
    try:
        data = json.loads(request.data.decode())
        for tea in data['number']:
            db.session.delete(Teacher.query.filter_by(number=tea).first())
        db.session.commit()
        return json.dumps({'code': 1})
    except:
        return json.dumps({'code': -1})


@admin.route('/user_admin')
@login_required
def user_admin():
    add_form_array = [{
        'text': '用户名',
        'name': 'user_name'
    }, {
        'text': '密码',
        'type': 'password',
        'name': 'password'
    }]
    update_form_array = [{
        'text': '用户名',
        'name': 'user_name'
    }]
    return render_template("user/admin.html", add_form_html=generate_form_html(add_form_array),
                           update_form_html=generate_form_html(update_form_array, mode='update'),
                           add_form_height=len(add_form_array) * 45 + 125,
                           update_form_height=len(update_form_array) * 45 + 125)


@admin.route('/load_admin')
@login_required
def load_admin():
    search_text = request.args.get('search_text', '')
    page_size = int(request.args.get('page_size', '10'))
    page_number = int(request.args.get('page_number', '1'))
    sort_name = request.args.get('sort_name', 'number')
    sort_order = request.args.get('sort_order', 'asc')

    if search_text == '':
        if sort_order == 'asc':
            pagination = Admin.query.order_by(db.asc(Admin.id)).paginate(page_number, page_size, False)
        else:
            pagination = Admin.query.order_by(db.desc(Admin.id)).paginate(page_number, page_size, False)
    else:
        if sort_order == 'asc':
            pagination = Admin.query.order_by(db.asc(Admin.id)).paginate(page_number, page_size, False)
        else:
            pagination = Admin.query.order_by(db.desc(Admin.id)).paginate(page_number, page_size, False)
    admins = []
    for item in pagination.items:
        admins.append({
            'id': item.id,
            'user_name': item.user_name,
            'create_time': item.create_time.strftime("%Y-%m-%d") if item.create_time else None
        })
    return json.dumps({
        "total": pagination.total,
        "rows": admins
    })


@admin.route('/user_add_admin', methods=['POST'])
@login_required
def user_add_admin():
    try:
        data = json.loads(request.data.decode())
        admin = Admin.query.filter_by(user_name=data["user_name"]).first()
        if admin:
            return json.dumps({'code': -1, 'msg': '用户名已存在'})
        db.session.add(Admin(user_name=data["user_name"], password=data["password"]))
        db.session.commit()
        return json.dumps({'code': 1, 'msg': '新增成功'})
    except:
        return json.dumps({'code': -1, 'msg': '新增失败'})


@admin.route('/user_delete_admin', methods=['POST'])
@login_required
def user_delete_admin():
    try:
        data = json.loads(request.data.decode())
        flag = False
        for admin in data['ids']:
            if current_user.id == admin:
                flag = True
                continue
            db.session.delete(Admin.query.filter_by(id=admin).first())
        db.session.commit()
        return json.dumps({'code': 1, 'flag': flag})
    except:
        return json.dumps({'code': -1})


@admin.route('/user_edit_admin', methods=['POST'])
@login_required
def user_edit_admin():
    try:
        data = json.loads(request.data.decode())
        admin = Admin.query.filter_by(user_name=data["user_name"]).first()
        if admin:
            return json.dumps({'code': -1, 'msg': '用户名已存在'})
        admin = Admin.query.filter_by(id=int(data["id"])).first()
        admin.user_name = data["user_name"]
        db.session.commit()
        return json.dumps({'code': 1, 'msg': '修改成功'})
    except Exception as e:
        return json.dumps({'code': -1, 'msg': '修改失败'})
