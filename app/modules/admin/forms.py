from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField("用户名", validators=[DataRequired(), Length(1, 64)])
    password = PasswordField("密码", validators=[DataRequired()])
    remember_me = BooleanField("记住登陆")
    submit = SubmitField("登陆")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码',
                             validators=[DataRequired(), EqualTo('password2', message='两次密码不匹配')])
    password2 = PasswordField('确认新密码', validators=[DataRequired()])
    submit = SubmitField('修改')
