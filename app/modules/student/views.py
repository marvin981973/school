import json

from app.modules.student import student
from flask import session, request

from app.models import Student, EstablishedCourse, AbsenceRecord, getXNXQ


@student.route("/")
def say_hello():
    return "I'm the student"


@student.route("/get_class_table")
def get_class_table():
    stu = Student(session['user_number'])
    return json.dumps(stu.get_class_table())


@student.route("/get_courses")
def get_courses():
    session["user_number"] = "149074064"
    stu = Student(session["user_number"])
    courses = stu.get_course()
    res = []
    for sel in courses:
        esc = EstablishedCourse.query.filter(EstablishedCourse.id == sel.established_course_id).first()
        course = esc.course.name
        class_time = esc.class_time
        course_time_ = ""
        class_time_details = class_time.split(';')
        for index in class_time_details:
            course_time_ += ('周' + index[:1] + '第' + index[-1:] + "节 ")
        grade = None
        if sel.final_grade:
            grade = sel.performance_score * (esc.daily_grade_ratio / 100) + sel.final_grade * (
                    1 - esc.daily_grade_ratio / 100)
        res.append({
            "course_place": esc.class_room,
            "course": course,
            "esc_id": esc.id,
            "course_time": course_time_,
            "course_teacher": esc.teacher.name,
            "daily_grade": sel.performance_score,
            "final_grade": sel.final_grade,
            "grade": grade

        })
    return json.dumps(res)


@student.route("/load_attendance_records")
def load_attendance_records():
    session["user_number"] = "149074064"
    mode = request.args.get("mode")
    res = []
    if mode == '0':
        esc_id = request.args.get("esc_id")
        records = AbsenceRecord.query.filter(AbsenceRecord.student_id == session["user_number"],
                                             AbsenceRecord.established_course_id == esc_id).all()
        record = []
        for re in records:
            record.append({
                "time": re.attendance.attendance_time.strftime("%Y-%m-%d %H:%M:%S"),
                "type": int(re.attendance.attendance_type),
                "count": re.attendance.attendance_count,
                "absence_type": int(re.absence_type)
            })

        res.append({
            'course': EstablishedCourse.query.filter(EstablishedCourse.id
                                                     == esc_id).first().course.name,
            'records': record
        })
    else:
        stu_number = session["user_number"]
        stu = Student(stu_number)
        courses = stu.get_course()
        for course in courses:
            records = AbsenceRecord.query.filter(AbsenceRecord.student_id == stu_number,
                                                 AbsenceRecord.established_course_id == course.established_course_id).all()
            record = []
            for re in records:
                record.append({
                    "time": re.attendance.attendance_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "type": int(re.attendance.attendance_type),
                    "count": re.attendance.attendance_count,
                    "absence_type": int(re.absence_type)
                })

            res.append({
                'course': EstablishedCourse.query.filter(
                    EstablishedCourse.id == course.established_course_id).first().course.name,
                'records': record
            })

    return json.dumps(res)
