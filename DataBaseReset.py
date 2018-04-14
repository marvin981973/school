from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import config
import json
import uuid
from datetime import datetime


app = Flask(__name__)
config_name = 'dev'
app.config.from_object(config[config_name])
config[config_name].init_app(app)

db = SQLAlchemy(app)



# 学院表
class College(db.Model):
    __tablename__ = 'college'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    name = db.Column(db.String(20))
    classes = db.relationship('Classes', backref='college', lazy='dynamic')
    students = db.relationship('Student', backref='college', lazy='dynamic')
    teachers = db.relationship('Teacher', backref='college', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<College %r>' % self.name


# 班级表
class Classes(db.Model):
    __tablename__ = 'classes'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    name = db.Column(db.String(20))
    nick_name = db.Column(db.String(20))
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    count = db.Column(db.Integer)
    college_id = db.Column(db.String(36), db.ForeignKey('college.id', ondelete='CASCADE', onupdate='CASCADE'))
    students = db.relationship('Student', backref='classes', lazy='dynamic')

    def __init__(self, name, nick_name='', count=0):
        self.name = name
        self.nick_name = nick_name
        self.count = count

    def __repr__(self):
        return '<Classes %r>' % self.name


# 学生表
class Student(db.Model):
    __tablename__ = 'student'

    number = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(20))
    age = db.Column(db.Integer)
    sex = db.Column(db.String(1))
    entrance_year = db.Column(db.Integer)
    classes_id = db.Column(db.String(36), db.ForeignKey('classes.id', ondelete='CASCADE', onupdate='CASCADE'))
    college_id = db.Column(db.String(36), db.ForeignKey('college.id', ondelete='CASCADE', onupdate='CASCADE'))
    birth_day = db.Column(db.DateTime)
    head_url = db.Column(db.String(50))
    telephone = db.Column(db.String(11))
    mail = db.Column(db.String(50))

    def __init__(self, number):
        self.number = number

    # 获取课程表
    def get_class_table(self):
        xn_xq = getXNXQ()
        courses = SelectedCourse.query.filter(SelectedCourse.student_id == self.number,
                                              SelectedCourse.school_year == xn_xq).all()
        res = []
        for cour in courses:
            established_course = EstablishedCourse.query.filter(
                EstablishedCourse.id == cour.established_course_id).first()
            teacher = established_course.teacher.name
            course = established_course.course.name
            class_time = established_course.class_time
            class_time_details = class_time.split(';')
            for index in class_time_details:
                c = {
                    "established_course_id": established_course.id,
                    "class_time": 'c_' + index[:1] + '_' + index[-1:],
                    "class_room": established_course.class_room,
                    "teacher": teacher,
                    "course": course
                }
                res.append(c)

        return res

    def __repr__(self):
        return '<Student %r>' % self.number


# 教师表
class Teacher(db.Model):
    __tablename__ = 'teacher'

    number = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(20))
    age = db.Column(db.Integer)
    sex = db.Column(db.String(1))
    college_id = db.Column(db.String(36), db.ForeignKey('college.id', ondelete='CASCADE', onupdate='CASCADE'))
    birth_day = db.Column(db.DateTime)
    head_url = db.Column(db.String(50))
    telephone = db.Column(db.String(11))
    mail = db.Column(db.String(50))
    education = db.Column(db.String(30))
    established_courses = db.relationship('EstablishedCourse', backref='teacher', lazy='dynamic')

    def __init__(self, number):
        self.number = number

    # 获得课程
    def get_class(self):
        courses = EstablishedCourse.query.filter(EstablishedCourse.teacher_id == self.number,
                                                 EstablishedCourse.school_year == getXNXQ()).all()
        return courses

    # 获取课程表
    def get_class_table(self):
        res = []
        established_course = self.get_class()
        for esc in established_course:
            course = esc.course.name
            class_time = esc.class_time
            class_time_details = class_time.split(';')
            for index in class_time_details:
                c = {
                    "established_course_id": esc.id,
                    "class_time": 'c_' + index[:1] + '_' + index[-1:],
                    "class_room": esc.class_room,
                    "teacher": self.name,
                    "course": course
                }
                res.append(c)
        return res

    def __repr__(self):
        return '<Teacher %r>' % self.number


# 用户绑定表
class UserBind(db.Model):
    __tablename__ = 'user_bind'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    openid = db.Column(db.String(36))
    number = db.Column(db.String(20))
    bind_time = db.Column(db.DateTime, nullable=False, default=datetime.now())
    identity_type = db.Column(db.String(5))
    is_available = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(self, openid, number, identity_type):
        self.openid = openid
        self.number = number
        self.identity_type = identity_type

    @staticmethod
    def check_bind(open_id):
        bind = UserBind.query.filter_by(openid=open_id).first()
        if bind:
            return json.dumps({'code': '1', 'msg': '', 'user_type': bind.identity_type})
        return json.dumps({'code': '0', 'msg': ''})

    def __validate_user(self):
        if self.query.filter_by(openid=self.openid).first():
            raise DataConflictException(u'用户已绑定')

        if self.identity_type == 's' and Student.query.filter(Student.number == self.number).first() == None:
            raise DataConflictException(u'学生账号不存在')

        if self.identity_type == 't' and Teacher.query.filter(Teacher.number == self.number).first() == None:
            raise DataConflictException(u'教师账号不存在')

    def bind(self):
        try:
            self.__validate_user()
            db.session.add(self)
            db.session.commit()
            return {'code': '1', 'msg': u'绑定成功'}
        except DataConflictException as e:
            return {'code': '-1', 'msg': str(e)}

    def __repr__(self):
        return '<UserBind %r>' % self.openid


# 课程表
class Course(db.Model):
    __tablename__ = 'course'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    name = db.Column(db.String(40))
    credit = db.Column(db.Float)
    category = db.Column(db.String(30))
    have_books = db.Column(db.Boolean, nullable=False, default=True)
    established_courses = db.relationship('EstablishedCourse', backref='course', lazy='dynamic')

    def __init__(self, name, credit, category, **other):
        self.name = name
        self.credit = credit
        self.category = category
        self.have_books = other.get('have_books')

    def __repr__(self):
        return '<Course %r>' % self.name


# 开课表
class EstablishedCourse(db.Model):
    __tablename__ = 'established_course'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    course_id = db.Column(db.String(36), db.ForeignKey('course.id', ondelete='CASCADE', onupdate='CASCADE'))
    capacity = db.Column(db.Integer)
    class_time = db.Column(db.String(30))
    class_room = db.Column(db.String(30))
    class_period = db.Column(db.Integer)
    teacher_id = db.Column(db.String(36), db.ForeignKey('teacher.number', ondelete='CASCADE', onupdate='CASCADE'))
    school_year = db.Column(db.String(15))

    def __init__(self, course_id, capacity, class_time, class_room, class_period, teacher_id, school_year):
        self.course_id = course_id
        self.capacity = capacity
        self.class_time = class_time
        self.class_room = class_room
        self.class_period = class_period
        self.teacher_id = teacher_id
        self.school_year = school_year

    def __repr__(self):
        return '<EstablishedCourse %r>' % self.id


# 选课表
class SelectedCourse(db.Model):
    __tablename__ = 'selected_course'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    established_course_id = db.Column(db.String(36),
                                      db.ForeignKey('established_course.id', ondelete='CASCADE', onupdate='CASCADE'))
    student_id = db.Column(db.String(36), db.ForeignKey('student.number', ondelete='CASCADE', onupdate='CASCADE'))
    performance_score = db.Column(db.Float, nullable=False, default=100)
    school_year = db.Column(db.String(15))

    def __repr__(self):
        return '<SelectedCourse %r>' % self.id


# 题库表
class QuestionBank(db.Model):
    __tablename__ = 'question_bank'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    description = db.Column(db.Text)
    answer = db.Column(db.String(36))
    score = db.Column(db.Float)
    course_id = db.Column(db.String(36), db.ForeignKey('course.id', ondelete='CASCADE', onupdate='CASCADE'))
    category = db.Column(db.String(10))
    add_time = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return '<QuestionBank %r>' % self.id


# 作业表
class HomeWork(db.Model):
    __tablename__ = 'homework'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    established_course_id = db.Column(db.String(36),
                                      db.ForeignKey('established_course.id', ondelete='CASCADE', onupdate='CASCADE'))
    course_id = db.Column(db.String(36), db.ForeignKey('course.id', ondelete='CASCADE', onupdate='CASCADE'))
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.now())
    end_time = db.Column(db.DateTime, nullable=False)
    questions_count = db.Column(db.Integer)
    questions = db.Column(db.Text)

    def __init__(self, established_course_id, course_id, questions_count, questions, **other):
        self.established_course_id = established_course_id
        self.course_id = course_id
        self.questions_count = questions_count
        self.questions = questions
        self.start_time = other.get('start_time')

    def __repr__(self):
        return '<HomeWork %r>' % self.id


# 作业提交表
class HomeWorkSubmit(db.Model):
    __tablename__ = 'homework_submit'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    homework_id = db.Column(db.String(36), db.ForeignKey('homework.id', ondelete='CASCADE', onupdate='CASCADE'))
    student_id = db.Column(db.String(36), db.ForeignKey('student.number', ondelete='CASCADE', onupdate='CASCADE'))
    submit_time = db.Column(db.DateTime, nullable=False, default=datetime.now())
    answer_list = db.relationship('HomeWorkSubmitAnswer', backref='homework_submit', lazy='dynamic')

    def __init__(self, homework_id, student_id):
        self.homework_id = homework_id
        self.student_id = student_id

    def __repr__(self):
        return '<HomeWorkSubmit %r>' % self.id


# 作业提交答案表
class HomeWorkSubmitAnswer(db.Model):
    __tablename__ = 'homework_submit_answer'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    homework_id = db.Column(db.String(36), db.ForeignKey('homework.id', ondelete='CASCADE', onupdate='CASCADE'))
    homework_submit_id = db.Column(db.String(36),
                                   db.ForeignKey('homework_submit.id', ondelete='CASCADE', onupdate='CASCADE'))
    question_id = db.Column(db.String(36), db.ForeignKey('question_bank.id', ondelete='CASCADE', onupdate='CASCADE'))
    answer = db.Column(db.Text)

    def __init__(self, homework_id, homework_submit_id, question_id, **other):
        self.homework_id = homework_id
        self.homework_submit_id = homework_submit_id
        self.question_id = question_id
        self.answer = other.get('answer')

    def __repr__(self):
        return '<HomeWorkSubmitAnswer %r>' % self.id


# 考勤记录
class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_record'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    established_course_id = db.Column(db.String(36),
                                      db.ForeignKey('established_course.id', ondelete='CASCADE', onupdate='CASCADE'))
    attendance_type = db.Column(db.String(10))
    attendance_count = db.Column(db.Integer)
    attendance_time = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __init__(self, established_course_id, attendance_type, attendance_count):
        self.established_course_id = established_course_id
        self.attendance_type = attendance_type
        self.attendance_count = attendance_count

    def __repr__(self):
        return '<AttendanceRecord %r>' % self.id


# 缺勤记录
class AbsenceRecord(db.Model):
    __tablename__ = 'absence_record'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    established_course_id = db.Column(db.String(36),
                                      db.ForeignKey('established_course.id', ondelete='CASCADE', onupdate='CASCADE'))
    attendance_record_id = db.Column(db.String(36),
                                     db.ForeignKey('attendance_record.id', ondelete='CASCADE', onupdate='CASCADE'))
    absence_type = db.Column(db.String(10))
    student_id = db.Column(db.String(36), db.ForeignKey('student.number', ondelete='CASCADE', onupdate='CASCADE'))

    def __init__(self, established_course_id, attendance_record_id, absence_type, student_id):
        self.established_course_id = established_course_id
        self.attendance_record_id = attendance_record_id
        self.absence_type = absence_type
        self.student_id = student_id

    def __repr__(self):
        return '<AbsenceRecord %r>' % self.id


# 失物招领
class LostFound(db.Model):
    __tablename__ = 'lost_found'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    add_time = db.Column(db.DateTime, nullable=False, default=datetime.now())
    publisher = db.Column(db.String(30))
    description = db.Column(db.Text)
    img_url = db.Column(db.String(50))
    status = db.Column(db.String(5), nullable=False, default='0')

    def __init__(self, publisher, description, img_url):
        self.publisher = publisher
        self.description = description
        self.img_url = img_url

    def __repr__(self):
        return '<LostFound %r>' % self.id


# 班级通知表
class ClassesNotification(db.Model):
    __tablename__ = 'classes_notification'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    classes_id = db.Column(db.String(36), db.ForeignKey('classes.id', ondelete='CASCADE', onupdate='CASCADE'))
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    content = db.Column(db.Text)

    def __init__(self, classes_id, content):
        self.classes_id = classes_id
        self.content = content

    def __repr__(self):
        return '<ClassesNotification %r>' % self.name


# 班级动态表
class ClassesDynamic(db.Model):
    __tablename__ = 'classes_dynamic'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    classes_id = db.Column(db.String(36), db.ForeignKey('classes.id', ondelete='CASCADE', onupdate='CASCADE'))
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    publisher = db.Column(db.String(30))
    content = db.Column(db.Text)
    img_list = db.Column(db.Text)

    def __init__(self, classes_id, publisher, content, img_list):
        self.classes_id = classes_id
        self.publisher = publisher
        self.content = content
        self.img_list = img_list

    def __repr__(self):
        return '<ClassesDynamic %r>' % self.name


# 班级相册表
class ClassesAlbum(db.Model):
    __tablename__ = 'classes_album'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    classes_id = db.Column(db.String(36), db.ForeignKey('classes.id', ondelete='CASCADE', onupdate='CASCADE'))
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    publisher = db.Column(db.String(30))
    img_list = db.Column(db.Text)

    def __init__(self, classes_id, publisher, img_list):
        self.classes_id = classes_id
        self.publisher = publisher
        self.img_list = img_list

    def __repr__(self):
        return '<ClassesAlbum %r>' % self.name


# 校园风光
class SchoolScenery(db.Model):
    __tablename__ = 'school_scenery'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    img_url = db.Column(db.String(100))
    description = db.Column(db.String(30))

    def __repr__(self):
        return '<SchoolScenery %r>' % self.description



def reset():
    db.drop_all()
    db.create_all()


if __name__ == '__main__':
    reset()
