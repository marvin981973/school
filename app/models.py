import json
import uuid
from datetime import datetime

from app import create_app_for_db, db

from app.tools.CustomException import DataConflictException
from app.tools import get_random


def getXNXQ():
    time_now = datetime.now()
    year = time_now.year
    month = time_now.month
    if 2 <= month <= 8:
        xn = "%d-%d" % (year - 1, year)
        xq = '2'
    elif month > 8:
        xn = "%d-%d" % (year, year + 1)
        xq = '1'
    else:
        xn = "%d-%d" % (year - 1, year)
        xq = '1'
    return xn + " " + xq


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
    signature = db.Column(db.String(50))
    age = db.Column(db.Integer)
    sex = db.Column(db.String(1))
    entrance_year = db.Column(db.Integer)
    classes_id = db.Column(db.String(36), db.ForeignKey('classes.id', ondelete='CASCADE', onupdate='CASCADE'))
    college_id = db.Column(db.String(36), db.ForeignKey('college.id', ondelete='CASCADE', onupdate='CASCADE'))
    birth_day = db.Column(db.DateTime)
    head_url = db.Column(db.String(50))
    telephone = db.Column(db.String(11))
    mail = db.Column(db.String(50))
    absence_records = db.relationship('AbsenceRecord', backref='student', lazy='dynamic')
    selected_courses = db.relationship('SelectedCourse', backref='student', lazy='dynamic')

    def __init__(self, number):
        self.number = number

    # 获取课程
    def get_course(self):
        courses = SelectedCourse.query.filter(SelectedCourse.student_id == self.number,
                                              SelectedCourse.school_year == getXNXQ()).all()
        return courses

    # 获取课程表
    def get_class_table(self):
        courses = self.get_course()
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
    signature = db.Column(db.String(50))
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

    # 获取考勤记录
    def get_attence_record(self, e_course_id, cur_page):
        pagination = AttendanceRecord.query.filter(AttendanceRecord.established_course_id == e_course_id).order_by(
            AttendanceRecord.attendance_time.desc()).paginate(
            cur_page, 10, False)
        has_next_page = (False if pagination.page == pagination.pages else True)
        records = []
        for item in pagination.items:
            absence = item.absences.count()
            records.append({
                "record_id": item.id,
                "type": item.attendance_type,
                "total": item.attendance_count,
                "time": item.attendance_time.strftime("%Y-%m-%d"),
                "absence": absence,
                "ratio": absence / item.attendance_count
            })
        return {"data": records, "has_next_page": has_next_page}

    # 获取缺勤学生
    def get_absence_stu(self, attendance_id):
        items = AbsenceRecord.query.filter(AbsenceRecord.attendance_record_id == attendance_id).all()
        absences = []
        for item in items:
            absences.append({
                "id": item.id,
                "student_id": item.student_id,
                "absence_type": int(item.absence_type),
                "stu_head": item.student.head_url,
                "stu_name": item.student.name,
                "stu_class_name": item.student.classes.name,
                "absence_count": AbsenceRecord.query.filter(AbsenceRecord.student_id == item.student_id,
                                                            AbsenceRecord.established_course_id == item.established_course_id,
                                                            AbsenceRecord.absence_type == '2').count(),

            })
        return {"data": absences}

    # 修改缺勤学生信息
    def modify_absence(self, absence_id, modify_type):
        try:
            absence = AbsenceRecord.query.filter(AbsenceRecord.id == absence_id).first()
            if modify_type == '3':
                db.session.delete(absence)
            else:
                absence.absence_type = modify_type
            db.session.commit()
            return {"code": 1}
        except:
            return {"code": -1}

    # 获取课程人数
    def get_student_count(self, e_course_id):
        return {"count": SelectedCourse.query.filter(SelectedCourse.established_course_id == e_course_id).count()}

    # 获取点名列表
    def get_attendance_members(self, e_course_id, attendance_type, attendance_count):
        students = SelectedCourse.query.filter(SelectedCourse.established_course_id == e_course_id).all()
        students_count = len(students)
        if attendance_type == '0':  # 随机
            out = get_random(attendance_count if attendance_count < students_count else students_count, students_count)
        else:
            out = [i for i in range(students_count)]
        data = []
        for i in out:
            stu = students[i].student
            data.append({
                "stu_id": stu.number,
                "name": stu.name,
                "c_name": stu.classes.name,
                "head_url": stu.head_url
            })
        return {"stu": data}

    # 保存点名记录
    def save_attendance(self, data):
        e_course = EstablishedCourse.query.filter(EstablishedCourse.id == data["established_course_id"]).first()
        auto_calculate_daily_grade = e_course.auto_calculate_daily_grade
        absence_minus_pt = e_course.absence_minus_pt
        attendance = AttendanceRecord(data["established_course_id"], data["attendance_type"],
                                      data["attendance_count"])
        id = str(uuid.uuid1())
        attendance.id = id
        try:
            attendance.save()
            school_year = getXNXQ()
            for stu in data["absences"]:
                s = AbsenceRecord(data["established_course_id"], id, stu["absence_type"], stu["stu_id"], school_year)
                s.id = str(uuid.uuid1())
                db.session.add(s)
                if auto_calculate_daily_grade:
                    select = SelectedCourse.query.filter(
                        SelectedCourse.established_course_id == data["established_course_id"],
                        SelectedCourse.student_id == stu["stu_id"]).first()
                    select.performance_score -= absence_minus_pt
                    db.session.add(select)
            db.session.commit()
            return {"code": 1}
        except:
            db.session.delete(attendance)
            db.session.commit()
            return {"code": -1}

    # 平时分评定
    def set_performance_score(self, e_course_id, stu, dailygrade):
        students = SelectedCourse.query.filter(SelectedCourse.established_course_id == e_course_id,
                                               SelectedCourse.student_id.in_(stu))
        try:
            for student in students:
                student.performance_score = dailygrade
                db.session.add(student)
            db.session.commit()
            return {"code": 1}
        except:
            return {"code": -1}

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
    auto_calculate_daily_grade = db.Column(db.Boolean, nullable=False, default=True)
    absence_minus_pt = db.Column(db.Integer, nullable=False, default=1)
    daily_grade_ratio = db.Column(db.Integer, nullable=False, default=20)

    def __init__(self, course_id, capacity, class_time, class_room, class_period, teacher_id, school_year):
        self.course_id = course_id
        self.capacity = capacity
        self.class_time = class_time
        self.class_room = class_room
        self.class_period = class_period
        self.teacher_id = teacher_id
        self.school_year = school_year

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<EstablishedCourse %r>' % self.id


# 课程通知表
class EstablishedCourseNotification(db.Model):
    __tablename__ = 'established_course_notification'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    established_course_id = db.Column(db.String(36),
                                      db.ForeignKey('established_course.id', ondelete='CASCADE', onupdate='CASCADE'))
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now())
    noti_title = db.Column(db.String(100))
    noti_content = db.Column(db.Text)
    read_count = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, established_course_id, noti_title, noti_content):
        self.established_course_id = established_course_id
        self.noti_title = noti_title
        self.noti_content = noti_content

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<EstablishedCourseNotification %r>' % self.id


# 选课表
class SelectedCourse(db.Model):
    __tablename__ = 'selected_course'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    established_course_id = db.Column(db.String(36),
                                      db.ForeignKey('established_course.id', ondelete='CASCADE', onupdate='CASCADE'))
    student_id = db.Column(db.String(36), db.ForeignKey('student.number', ondelete='CASCADE', onupdate='CASCADE'))
    performance_score = db.Column(db.Float, nullable=False, default=100)
    school_year = db.Column(db.String(15))
    final_grade = db.Column(db.Float)

    def __repr__(self):
        return '<SelectedCourse %r>' % self.id


# 考勤记录
class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_record'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    established_course_id = db.Column(db.String(36),
                                      db.ForeignKey('established_course.id', ondelete='CASCADE', onupdate='CASCADE'))
    attendance_type = db.Column(db.String(10))
    attendance_count = db.Column(db.Integer)
    attendance_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    absences = db.relationship('AbsenceRecord', backref='attendance', lazy='dynamic')

    def __init__(self, established_course_id, attendance_type, attendance_count):
        self.established_course_id = established_course_id
        self.attendance_type = attendance_type
        self.attendance_count = attendance_count

    def save(self):
        db.session.add(self)
        db.session.commit()

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
    school_year = db.Column(db.String(15))

    def __init__(self, established_course_id, attendance_record_id, absence_type, student_id, school_year):
        self.established_course_id = established_course_id
        self.attendance_record_id = attendance_record_id
        self.absence_type = absence_type
        self.student_id = student_id
        self.school_year = school_year

    def __repr__(self):
        return '<AbsenceRecord %r>' % self.id


# 失物招领
class LostFound(db.Model):
    __tablename__ = 'lost_found'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    add_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    publisher = db.Column(db.String(30))
    publisher_name = db.Column(db.String(30))
    title = db.Column(db.String(30))
    description = db.Column(db.Text)
    img_url = db.Column(db.String(50))
    status = db.Column(db.String(5), nullable=False, default='0')

    def __init__(self, publisher, publisher_name, title, description, img_url):
        self.publisher = publisher
        self.title = title
        self.publisher_name = publisher_name
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


# 校园动态表
class SchoolDynamic(db.Model):
    __tablename__ = 'school_dynamic'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    publisher_number = db.Column(db.String(20))
    publisher_type = db.Column(db.String(5))
    add_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    content = db.Column(db.Text)
    imges = db.Column(db.String(500))

    def __init__(self, publisher_number, publisher_type, content, imges):
        self.publisher_number = publisher_number
        self.publisher_type = publisher_type
        self.content = content
        self.imges = imges

    def __repr__(self):
        return '<SchoolDynamic %r>' % self.id


# 评论表
class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    parent_id = db.Column(db.String(36))
    commenter = db.Column(db.String(20))
    commenter_type = db.Column(db.String(5))
    add_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    content = db.Column(db.Text)
    type = db.Column(db.String(5))  # 0 校园动态评论 1 班级动态评论

    def __init__(self, parent_id, commenter, commenter_type, content, type):
        self.parent_id = parent_id
        self.commenter = commenter
        self.commenter_type = commenter_type
        self.content = content
        self.type = type

    def __repr__(self):
        return '<Comment %r>' % self.id


# 收藏表
class Collection(db.Model):
    __tablename__ = 'collection'

    id = db.Column(db.String(36), primary_key=True, nullable=False, default=str(uuid.uuid1()))
    collection_id = db.Column(db.String(36))
    collector = db.Column(db.String(20))
    collector_type = db.Column(db.String(5))
    add_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    type = db.Column(db.String(5))  # 0收藏校园动态

    def __init__(self, collection_id, collector, collector_type, type):
        self.collection_id = collection_id
        self.collector = collector
        self.collector_type = collector_type
        self.type = type

    def __repr__(self):
        return '<Collection %r>' % self.id


if __name__ == "__main__":
    db.create_all(app=create_app_for_db())
