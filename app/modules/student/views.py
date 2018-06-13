import json

from app import db
from app.modules.student import student
from flask import session, request

from app.models import Student, EstablishedCourse, AbsenceRecord, getXNXQ, EstablishedCourseNotificationCheck, Classes


@student.route("/")
def say_hello():
    return "I'm the student"


@student.route("/get_class_table")
def get_class_table():
    stu = Student(session['user_number'])
    return json.dumps(stu.get_class_table())


@student.route("/get_courses")
def get_courses():
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
    mode = request.args.get("mode")
    res = []
    absences = AbsenceRecord.query.filter(AbsenceRecord.student_id == session["user_number"],
                                          AbsenceRecord.school_year == getXNXQ(),
                                          AbsenceRecord.checked == False).all()
    for absence in absences:
        absence.checked = True
    db.session.commit()
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


@student.route('/check_course_notification')
def check_course_notification():
    try:
        check = EstablishedCourseNotificationCheck.query.filter(
            EstablishedCourseNotificationCheck.id == request.args.get('check_id')).first()
        check.status = True
        db.session.commit()
        return json.dumps({'code': 1})
    except:
        return json.dumps({'code': -1})


@student.route('/get_class_info')
def get_class_info():
    try:
        classes = Student.query.filter(Student.number == session["user_number"]).first().classes
        students = classes.students.paginate(1, 10, False).items
        return json.dumps({'class': {
            'id': classes.id,
            'name': classes.name,
            'nick_name': classes.nick_name,
            'create_time': classes.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            'count': classes.students.count(),
            'college_name': classes.college.name,
            'students': [{'head_img': i.head_url, 'name': i.name} for i in students]
        }})
    except Exception as e:
        return json.dumps({'code': -1})


@student.route('/get_all_students')
def get_all_students():
    try:
        students = Student.query.filter(Student.classes_id == request.args.get('class_id')).all()
        return json.dumps({'students': [{
            'head_img': i.head_url,
            'name': i.name,
            'number': i.number
        } for i in students]})
    except Exception as e:
        return json.dumps({'code': -1})
