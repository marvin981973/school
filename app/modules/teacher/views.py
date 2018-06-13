import uuid

from app import db
from app.modules.teacher import teacher

from flask import session, request
import json
from app.models import Teacher, AttendanceRecord, EstablishedCourse, SelectedCourse, EstablishedCourseNotification, \
    EstablishedCourseNotificationCheck


@teacher.route("/")
def say_hello():
    return "I'm the teacher"


def init_teacher():
    # session['user_number'] = '1290'
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


@teacher.route("/get_dailygrade_setting")
def get_dailygrade_setting():
    e_course_id = request.args.get("e_course_id")
    e_course = EstablishedCourse.query.filter(EstablishedCourse.id == e_course_id).first()
    return json.dumps({
        "auto": e_course.auto_calculate_daily_grade,
        "queqin": e_course.absence_minus_pt,
        "zuoye": e_course.daily_grade_ratio
    })


@teacher.route("/modify_dailygrade_setting")
def modify_dailygrade_setting():
    e_course_id = request.args.get("e_course_id")
    e_course = EstablishedCourse.query.filter(EstablishedCourse.id == e_course_id).first()
    e_course.auto_calculate_daily_grade = "true" == request.args.get("switch_checked")
    e_course.absence_minus_pt = int(request.args.get("queqin_value"))
    e_course.daily_grade_ratio = int(request.args.get("zuoye_value"))
    e_course.save()
    return json.dumps({"code": 1})


@teacher.route("/get_students")
def get_students():
    e_course_id = request.args.get("e_course_id")
    students = SelectedCourse.query.filter(SelectedCourse.established_course_id == e_course_id).all()
    e_course = EstablishedCourse.query.filter(EstablishedCourse.id == e_course_id).first()
    res = []
    for stu in students:
        grade = None
        if stu.final_grade:
            grade = round(stu.performance_score * (e_course.daily_grade_ratio / 100) + stu.final_grade * (
                    1 - e_course.daily_grade_ratio / 100), 1)
        res.append({
            "name": stu.student.name,
            "head": stu.student.head_url,
            "c_name": stu.student.classes.name,
            "stu_id": stu.student_id,
            "f_grade": stu.final_grade,
            "p_grade": stu.performance_score,
            "c_grade": grade
        })
    return json.dumps(res)


@teacher.route("/set_performance_score", methods=["POST"])
def set_performance_score():
    tea = init_teacher()
    data = json.loads(request.data.decode())
    return json.dumps(tea.set_performance_score(data["e_course_id"], data["stu"], int(data["dailygrade"])))


@teacher.route("/load_e_course_nitification")
def load_e_course_nitification():
    e_course_id = request.args.get("e_course_id")
    notifications = EstablishedCourseNotification.query.filter(
        EstablishedCourseNotification.established_course_id == e_course_id).order_by(
        db.desc(EstablishedCourseNotification.create_time)).all()
    res = [{
        "id": noti.id,
        "noti_title": noti.noti_title,
        "create_time": noti.create_time.strftime("%Y-%m-%d"),
        "read_count": noti.read_count
    } for noti in notifications]
    return json.dumps(res)


@teacher.route("/delete_noti")
def delete_noti():
    id = request.args.get("id")
    notifications = EstablishedCourseNotification.query.filter(
        EstablishedCourseNotification.id == id).first()
    db.session.delete(notifications)
    db.session.commit()
    return json.dumps({"code": 1})


@teacher.route("/load_noti_content")
def load_noti_content():
    id = request.args.get("id")
    notifications = EstablishedCourseNotification.query.filter(
        EstablishedCourseNotification.id == id).first()
    notifications.read_count += 1
    db.session.add(notifications)
    db.session.commit()
    return json.dumps(
        {"code": 1, "title": notifications.noti_title, "time": notifications.create_time.strftime("%Y-%m-%d"),
         "content": notifications.noti_content}) if notifications else json.dumps({"code": -1})


@teacher.route("/add_noti", methods=["POST"])
def add_noti():
    data = json.loads(request.data.decode())
    notification_id = str(uuid.uuid1())
    notification = EstablishedCourseNotification(data["e_course_id"], data["form"]["title"], data["form"]["content"])
    notification.id = notification_id
    db.session.add(notification)
    students = SelectedCourse.query.filter(SelectedCourse.established_course_id == data["e_course_id"]).all()
    for stu in students:
        check = EstablishedCourseNotificationCheck(notification_id, stu.student_id)
        check.id = str(uuid.uuid1())
        db.session.add(check)
    db.session.commit()
    return json.dumps({"code": 1})


@teacher.route("/save_final_grade", methods=["POST"])
def save_final_grade():
    data = json.loads(request.data.decode())
    for key in data["grade"]:
        s_course = SelectedCourse.query.filter(SelectedCourse.student_id == key,
                                               SelectedCourse.established_course_id == data["e_course_id"]).first()
        s_course.final_grade = float(data["grade"][key])
    db.session.commit()
    return json.dumps({"code": 1})
