import os
import uuid

import datetime
from lxml import etree
from PIL import Image

from app import db
from app.modules.public import public

import json

from flask import Response, request, session

from app.modules.weather.weather import Weather

from app.config import wx_config

from app.tools.WebPageParsing import ScrapyPage
from app.models import UserBind, SchoolScenery, Teacher, Student, Comment, Dynamics, AbsenceRecord, getXNXQ, \
    EstablishedCourseNotificationCheck, EstablishedCourseNotification, Notification, EstablishedCourse, Feedback


@public.route('/')
def hello():
    return "Hello World"


@public.route('/image/<image_id>')
def get_image(image_id):
    image = open('app/static/images/{}'.format(image_id), 'rb')
    return Response(image, mimetype='image/jpeg')


def init_notification():
    res = {}
    res["comment_count"] = Comment.query.join(Dynamics, Comment.parent_id == Dynamics.id).filter(
        Dynamics.publisher_number == session["user_number"], Comment.checked == False).count()
    if session["user_type"] == 's':
        res["absence_count"] = AbsenceRecord.query.filter(AbsenceRecord.student_id == session["user_number"],
                                                          AbsenceRecord.school_year == getXNXQ(),
                                                          AbsenceRecord.checked == False).count()
        res["course_notification"] = EstablishedCourseNotificationCheck.query.filter(
            EstablishedCourseNotificationCheck.user_number == session["user_number"],
            EstablishedCourseNotificationCheck.status == False).count()

    return res


@public.route('/check_user', methods=['POST'])
def check_user():
    login_code = json.loads(request.data.decode())
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid=' + wx_config['appid'] + '&secret=' + wx_config[
        'secret'] + '&grant_type=authorization_code&js_code=' + login_code['code']
    try:
        open_id = json.loads(ScrapyPage(url))['openid']
        bind = UserBind.query.filter(UserBind.openid == open_id).first()
        if bind:
            session['user_number'] = bind.number
            session['user_type'] = bind.identity_type
            return json.dumps(
                {'code': '1', 'msg': '', 'user_type': bind.identity_type, 'user_number': bind.number,
                 'notification': init_notification()})
        session['open_id'] = open_id
        return json.dumps({'code': '0', 'msg': ''})
    except:
        return json.dumps({'code': '-1', 'msg': '用户验证失败...'})


@public.route('/bind_user', methods=['POST'])
def bind_user():
    form_value = json.loads(request.data.decode())
    try:
        user = UserBind(session['open_id'], form_value['number'], form_value['identity'])
        res = user.bind()
        if res["code"] == '1':
            session["user_number"] = form_value['number']
            session["user_type"] = form_value['identity']
        return json.dumps(res)
    except KeyError:
        return json.dumps({'code': '0', 'msg': '绑定失败'})


@public.route('/unbind_user')
def unbind_user():
    try:
        user = UserBind.query.filter(UserBind.number == session["user_number"]).first()
        db.session.delete(user)
        db.session.commit()
        return json.dumps({"code": 1})
    except:
        return json.dumps({"code": -1})


@public.route('/get_user_type')
def get_user_type():
    return json.dumps({"user_type": session["user_type"]})


@public.route('/get_week')
def get_week():
    try:
        html = ScrapyPage('http://211.70.149.139:84/jxz.aspx')
        selector = etree.HTML(html)
        tr = selector.xpath("//table/tr")[1]
        week = tr.xpath("./td/font/text()")[0].strip()
        return json.dumps({'code': 1, 'week': week})
    except:
        return json.dumps({'code': -1})


@public.route('/get_weather')
def get_weather():
    res = Weather.get_weather(request.args.get('lon'), request.args.get('lat'))
    return json.dumps(res)


@public.route('/school_scenery')
def school_scenery():
    cur_page = int(request.args.get("page"))
    pagination = SchoolScenery.query.paginate(cur_page, 10, False)
    has_next_page = (False if pagination.page == pagination.pages else True)
    data = []
    for item in pagination.items:
        data.append({
            "url": item.img_url,
            "description": item.description
        })
    return json.dumps({"has_next_page": has_next_page, "data": data})


@public.route("/get_user_info")
def get_user_info():
    user_number = request.args.get('user_number')
    user = Student.query.filter(Student.number == user_number).first()
    user_type = 's'
    if user is None:
        user = Teacher.query.filter(Teacher.number == user_number).first()
        user_type = 't'
    return json.dumps({
        "img_url": user.head_url,
        "name": user.name,
        "signature": user.signature,
        "number": user.number,
        "age": user.age,
        "sex": user.sex,
        "college": user.college.name,
        "classes": user.classes.name if user_type == 's' else None,
        'mail': user.mail,
        'hobbies': user.hobbies,
        'hometown': user.hometown,
        'profile_permission': user.profile_permission,
        'telephone': user.telephone,
        "birth_day": user.birth_day.strftime(
            "%Y-%m-%d") if user.birth_day else (datetime.datetime.now() - datetime.timedelta(
            days=365 * user.age)).strftime("%Y-%m-%d"),

    })


@public.route("/upload_user_head", methods=["POST"])
def upload_user_head():
    path = os.path.abspath(os.path.join(os.getcwd(), './app/upload/user/images/'))
    if not os.path.exists(path):
        os.makedirs(path)
    file = request.files["file"]
    file_name = str(uuid.uuid1()) + "." + file.filename.split(".")[-1:][0]
    save_path = path + "/" + file_name
    file.save(save_path)
    img = Image.open(save_path)
    height = img.size[1]
    width = img.size[0]
    crop_width = width if width < height else height
    if width < height:
        temp = height // 2 - crop_width // 2
        region = (0, temp, crop_width, temp + crop_width)
    else:
        temp = width // 2 - crop_width // 2
        region = (temp, 0, temp + crop_width, crop_width)
    cropImg = img.crop(region)
    cropImg.thumbnail((200, 200))
    cropImg.save(save_path)
    user_number = request.form["user"]
    user = Student.query.filter(Student.number == user_number).first()
    if user is None:
        user = Teacher.query.filter(Teacher.number == user_number).first()
    try:
        os.remove(path + "/" + user.head_url)
    except:
        pass
    user.head_url = file_name
    db.session.commit()
    return json.dumps({"code": 1, "file_name": file_name})


@public.route('/user_head/<image_id>')
def user_head(image_id):
    try:
        image = open('app/upload/user/images/{}'.format(image_id), 'rb')
        return Response(image, mimetype='image/jpeg')
    except:
        return None;


@public.route("/save_user_info")
def save_user_info():
    try:
        user_number = session["user_number"]
        user_type = session["user_type"]
        user = Teacher.query.filter(
            Teacher.number == user_number).first() if user_type == 't' else Student.query.filter(
            Student.number == user_number).first()
        setattr(user, request.args.get('name'),
                datetime.datetime.strptime(request.args.get('value'), "%Y-%m-%d") if request.args.get(
                    'name') == 'birth_day' else request.args.get('value'))
        db.session.commit()
        return json.dumps({"code": 1})
    except Exception as e:
        return json.dumps({"code": -1})


@public.route("/get_school_calendar")
def get_school_calendar():
    base_url = "http://jwc.ahut.edu.cn"
    static_url = base_url + '/list.jsp?urltype=tree.TreeTempUrl&wbtreeid=1109'
    html = ScrapyPage(static_url)
    selector = etree.HTML(html)
    calendars = selector.xpath("//a[@class='c44456']")
    data = []
    for calendar in calendars:
        selectot_cal = etree.HTML(ScrapyPage(base_url + calendar.xpath("./@href")[0].strip()))
        images = []
        for cal in selectot_cal.xpath("//div[@id='vsb_content']/p"):
            images.append(base_url + "/" + cal.xpath("./img/@src")[0])
        data.append({
            "name": calendar.xpath("./@title")[0].strip(),
            "images": images
        })
    return json.dumps({"data": data})


@public.route("/check_unread_message")
def check_unread_message():
    return json.dumps({"notification": init_notification()})


@public.route("/get_unread_message")
def get_unread_message():
    unread_comments = Comment.query.join(Dynamics, Comment.parent_id == Dynamics.id).filter(
        Dynamics.publisher_number == session["user_number"], Comment.checked == False).all()
    unread_course_notifications = EstablishedCourseNotificationCheck.query.filter(
        EstablishedCourseNotificationCheck.user_number == session["user_number"],
        EstablishedCourseNotificationCheck.status == False).all()
    messages = []
    for comment in unread_comments:
        dynamic = Dynamics.query.filter(Dynamics.id == comment.parent_id).first()
        messages.append({
            "type": '0',
            'commenter': comment.commenter,
            'commenter_head': Student.query.filter_by(
                number=comment.commenter).first().head_url if comment.commenter_type == 's' else Teacher.query.filter_by(
                number=comment.commenter).first().head_url,
            'time': comment.add_time.strftime("%Y-%m-%d %H:%M:%S"),
            'content': comment.content,
            'id': comment.id,
            'dynamic_type': comment.type,
            'dynamic_id': dynamic.id,
            'dynamic_summarize': dynamic.content
        })
    for course_notification in unread_course_notifications:
        notification = EstablishedCourseNotification.query.filter_by(id=course_notification.notification_id).first()
        e_course = EstablishedCourse.query.filter_by(id=notification.established_course_id).first()
        messages.append({
            "type": '1',
            "id": course_notification.id,
            "create_time": notification.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "notification_id": notification.id,
            "noti_title": notification.noti_title,
            "course": e_course.course.name,
            "teacher": e_course.teacher.name,
            "teacher_head": e_course.teacher.head_url,

        })
    return json.dumps({"data": messages})


@public.route('/get_system_message')
def get_system_message():
    cur_page = int(request.args.get("page"))
    pagination = Notification.query.order_by(db.desc(Notification.create_time)).paginate(
        cur_page, 10, False)
    has_next_page = (False if pagination.page == pagination.pages else True)
    data = []
    for item in pagination.items:
        data.append({
            "create_time": item.create_time.strftime("%Y-%m-%d"),
            "title": item.title,
            "content": item.content
        })
    return json.dumps({"has_next_page": has_next_page, "data": data})


@public.route("/add_feedback", methods=["POST"])
def add_feedback():
    try:
        name = Student.query.filter_by(number=session["user_number"]).first().name if session[
                                                                                          "user_type"] == 's' else Teacher.query.filter_by(
            number=session['user_number']).first().name
        feedback = Feedback(session["user_number"], name, json.loads(request.data.decode())['feedback'])
        feedback.id = str(uuid.uuid1())
        db.session.add(feedback)
        db.session.commit()
        return json.dumps({"code": 1})
    except Exception as e:
        return json.dumps({"code": -1})


if __name__ == "__main__":
    init_notification()
