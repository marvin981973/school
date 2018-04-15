from app.modules.teacher import teacher

from flask import session, request
import json
from app.models import Teacher, AttendanceRecord


@teacher.route("/")
def say_hello():
    return "I'm the teacher"


@teacher.route("/get_class_table")
def get_class_table():
    tea = Teacher(session['user_number'])
    return json.dumps(tea.get_class_table())


@teacher.route("/get_courses")
def get_courses():
    session['user_number'] = '1290'
    tea = Teacher(session['user_number'])
    courses = tea.get_class()
    res = []
    for esc in courses:
        course = esc.course.name
        class_time = esc.class_time
        course_time_ = ""
        class_time_details = class_time.split(';')
        for index in class_time_details:
            course_time_ += ('周' + index[:1] + '第' + index[-1:] + "节 ")
        res.append({
            "course_place": esc.class_room,
            "kaoqin_count": AttendanceRecord.query.filter(AttendanceRecord.established_course_id == esc.id).count(),
            "course": course,
            "esc_id": esc.id,
            "course_time": course_time_
        })
    return json.dumps(res)


@teacher.route("/get_attence_record")
def get_attence_record():
    session["user_number"] = '1290'
    tea = Teacher(session['user_number'])
    e_course_id = request.args.get("e_course_id")
    cur_page = int(request.args.get("page"))
    return json.dumps(tea.get_attence_record(e_course_id, cur_page))
