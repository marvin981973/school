import json

from app import db
from app.tools import generate_form_html
from . import admin
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, login_user, logout_user
from .forms import LoginForm
from app.models import Admin, Student


@admin.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(user_name=form.username.data).first()
        if admin is not None and admin.verify_password(form.password.data):
            login_user(admin, form.remember_me.data)
            return redirect(url_for('admin.index'))
        flash('用户名或密码错误')
    return render_template("login.html", form=form)


@admin.route('/')
@login_required
def index():
    return render_template('base.html')


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
    }], [{
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
        'category': 'select',
        'text': '班级',
        'name': 'classes',
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
    }], {
        'text': 'sdsdsdsd',
        'name': 'sdsdfsdfsd'
    }]
    return render_template("user/student.html", add_form_html=generate_form_html(form_array),
                           form_height=len(form_array) * 45 + 125)


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


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    flash('注销成功')
    return redirect(url_for('admin.login'))
