from app import db
from . import admin
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from .forms import LoginForm, ChangePasswordForm
from app.models import Admin


@admin.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(user_name=form.username.data).first()
        if admin is not None and admin.verify_password(form.password.data):
            login_user(admin, form.remember_me.data)
            return redirect(url_for('admin.index'))
        flash('用户名或密码错误')

    # db.session.add(Admin(user_name='shuai', password='187125'))
    # db.session.commit();
    return render_template("login.html", form=form)


@admin.route('/')
@login_required
def index():
    return render_template('base.html')


@admin.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('密码修改成功.')
            return redirect(url_for('admin.login'))
        else:
            flash('密码错误.')
    return render_template("change_password.html", form=form)


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    flash('注销成功')
    return redirect(url_for('admin.login'))
