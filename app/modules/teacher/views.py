from app.modules.teacher import teacher

from flask import session, request
import json
from app.models import Teacher, AttendanceRecord


@teacher.route("/")
def say_hello():
    return "I'm the teacher"


def init_teacher():
    session['user_number'] = '1290'
    return Teacher(session["user_number"])


@teacher.route("/get_class_table")
def get_class_table():
    tea = init_teacher()
    return json.dumps(tea.get_class_table())


@teacher.route("/get_courses")
def get_courses():
    tea = init_teacher()
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
    tea = init_teacher()
    e_course_id = request.args.get("e_course_id")
    cur_page = int(request.args.get("page"))
    return json.dumps(tea.get_attence_record(e_course_id, cur_page))


@teacher.route("/get_absence_stu")
def get_absence_stu():
    tea = init_teacher()
    attendance_id = request.args.get("attendance_id")
    return json.dumps(tea.get_absence_stu(attendance_id))


@teacher.route("/modify_absence")
def modify_absence():
    tea = init_teacher()
    absence_id = request.args.get("absence_id")
    modify_type = request.args.get("type")
    return json.dumps(tea.modify_absence(absence_id, modify_type))


@teacher.route("/get_student_count")
def get_student_count():
    tea = init_teacher()
    e_course_id = request.args.get("e_course_id")
    return json.dumps(tea.get_student_count(e_course_id))


@teacher.route("/get_attendance_members")
def get_attendance_members():
    tea = init_teacher()
    e_course_id = request.args.get("e_course_id")
    attendance_type = request.args.get("type")
    attendance_count = request.args.get("attendance_count")
    return json.dumps(tea.get_attendance_members(e_course_id, attendance_type, int(attendance_count)))


@teacher.route("/save_attendance", methods=["POST"])
def save_attendance():
    tea = init_teacher()
    data = json.loads(request.data.decode())
    return json.dumps(tea.save_attendance(data))


@teacher.route("/set_performance_score", methods=["POST"])
def set_performance_score():
    tea = init_teacher()
    data = json.loads(request.data.decode())
    return json.dumps(tea.set_performance_score(data["e_course_id"], data["stu"], int(data["dailygrade"])))
