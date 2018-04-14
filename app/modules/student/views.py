import json

from app.modules.student import student
from flask import session

from app.models import Student


@student.route("/")
def say_hello():
    return "I'm the student"


@student.route("/get_class_table")
def get_class_table():
    stu = Student(session['user_number'])
    return json.dumps(stu.get_class_table())
