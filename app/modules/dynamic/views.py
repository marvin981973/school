import uuid

import os

from PIL import Image

from app import db
from app.models import Dynamics, Student, Teacher, Comment, Collection
from app.modules.dynamic import dynamic
import json
from flask import request, session, Response
from lxml import etree
from app.tools.WebPageParsing import ScrapyPage


@dynamic.route('/get_news_list', methods=['POST'])
def get_news_list():
    content = json.loads(request.data.decode())
    mode = content["mode"]
    static_url = 'http://news.ahut.edu.cn/list.jsp' if mode == "0" else 'http://jwc.ahut.edu.cn/list.jsp'

    html = ScrapyPage(static_url + content['nextPageUrl'])
    selector = etree.HTML(html)
    news = selector.xpath("//a[@class='" + ("c1022" if mode == "0" else "c44456") + "']")
    try:
        next_page = selector.xpath("//a[@class='Next']/@href")[0]
    except IndexError:
        next_page = '-1'

    res = []
    for new in news:
        data = {
            "mode": mode,
            "href": new.xpath("./@href")[0],
            "title": new.xpath("./text()")[0].strip(),
            "time": new.xpath("../following-sibling::td[1]/text()")[0][:-1] if mode == "0" else
            new.xpath("../following-sibling::td[1]/text()")[0][1:-2]
        }
        res.append(data)
    return json.dumps({"news": res, 'nextPageUrl': next_page})


@dynamic.route('/get_news_content', methods=['POST'])
def get_news_content():
    content = json.loads(request.data.decode())
    host = 'http://news.ahut.edu.cn' if content["mode"] == "0" else 'http://jwc.ahut.edu.cn'
    content_url = content["contentUrl"]
    html = ScrapyPage(host + content_url)
    selector = etree.HTML(html)

    paragraph = selector.xpath("//div[@id='vsb_content']/p")
    if not paragraph:
        paragraph = selector.xpath("//div[@id='vsb_content_501']/p")
    content = []
    for p in paragraph:
        text = p.xpath("string(.)").strip().replace("\r\n", "").replace(" ", '')
        if text:
            content.append({"text": text, "type": 0})

        imgs = p.xpath(".//img")
        for img in imgs:
            content.append({"url": host + "/" + img.xpath("./@src")[0], "type": 1})
    return json.dumps({'content': content})


def format_dynamic(items):
    data = []
    for item in items:
        imgs = item.imges.split("#")
        images = []
        index = 0
        length = len(imgs)
        for i in range(int(length / 3 + 1)):
            temp = []
            for j in range(3):
                temp.append(imgs[index])
                index += 1
                if length == index:
                    break;
            images.append(temp)
            if length == index:
                break;
        user = Student.query.filter(
            Student.number == item.publisher_number).first() if item.publisher_type == 's' else Teacher.query.filter(
            Teacher.number == item.publisher_number).first()
        collection = Collection.query.filter(Collection.type == item.type, Collection.collection_id == item.id,
                                             Collection.collector == session["user_number"]).first()
        heart_count = Collection.query.filter(Collection.collection_id == item.id).count()
        data.append({
            "id": item.id,
            "time": item.add_time.strftime("%Y-%m-%d %H:%M:%S"),
            "content": item.content,
            "heart_count": heart_count,
            "publisher_number": item.publisher_number,
            "publisher_name": user.name,
            "head_url": user.head_url,
            "have_img": imgs[0] != '',
            "images": images,
            "dynamic_type": item.type,
            "comment_count": Comment.query.filter(Comment.parent_id == item.id,
                                                  Comment.type == item.type).count(),
            "collection_id": collection.id if collection else ""
        })
    return data


@dynamic.route('/get_school_dynamic')
def get_school_dynamic():
    cur_page = int(request.args.get("page"))
    pagination = Dynamics.query.filter(Dynamics.type == '0').order_by(db.desc(Dynamics.add_time)).paginate(cur_page, 20,
                                                                                                           False)
    has_next_page = (False if pagination.page == pagination.pages else True)
    data = format_dynamic(pagination.items)
    return json.dumps({"has_next_page": has_next_page, "data": data})


@dynamic.route('/images/<image_id>')
def image(image_id):
    image = open('app/upload/dynamic/images/{}'.format(image_id), 'rb')
    return Response(image, mimetype='image/jpeg')


@dynamic.route('/uncollect_dynamic')
def uncollect_school_dynamic():
    try:
        collection = Collection.query.filter(Collection.id == request.args.get('collection_id')).first()
        db.session.delete(collection)
        db.session.commit()
        return json.dumps({'code': 1})
    except:
        return json.dumps({"code": -1})


@dynamic.route('/collect_dynamic')
def collect_school_dynamic():
    try:
        collection = Collection(request.args.get("collection_id"), session["user_number"], session["user_type"],
                                request.args.get('dynamic_type'))
        id = str(uuid.uuid1())
        collection.id = id
        db.session.add(collection)
        db.session.commit()
        return json.dumps({'code': 1, "id": id})
    except:
        return json.dumps({"code": -1})


@dynamic.route('/load_dynamic_detail')
def load_dynamic_detail():
    dynamic = Dynamics.query.filter(Dynamics.id == request.args.get("id")).first()
    return json.dumps({"data": format_dynamic([dynamic])})


@dynamic.route('/load_comment')
def load_comment():
    cur_page = int(request.args.get("page"))
    id = request.args.get("id")
    pagination = Comment.query.filter(Comment.parent_id == id).order_by(db.desc(Comment.add_time)).paginate(cur_page,
                                                                                                            10, False)
    has_next_page = (False if pagination.page == pagination.pages else True)
    data = []
    for item in pagination.items:
        commenter = Student.query.filter(
            Student.number == item.commenter).first() if item.commenter_type == 's' else Teacher.query.filter(
            Teacher.number == item.commenter).first()
        data.append({
            "id": item.id,
            "head_url": commenter.head_url,
            "commenter": item.commenter,
            "commenter_name": commenter.name,
            "time": item.add_time.strftime("%Y-%m-%d %H:%M:%S"),
            "comment": item.content
        })
    return json.dumps({"has_next_page": has_next_page, "data": data})


@dynamic.route('/comment', methods=['POST'])
def comment():
    try:
        data = json.loads(request.data.decode())
        comment = Comment(data["id"], session["user_number"], session["user_type"], data["comment"],
                          data['dynamic_type'])
        comment.id = str(uuid.uuid1())
        db.session.add(comment)
        db.session.commit()
        return json.dumps({'code': 1})
    except:
        return json.dumps({'code': -1})


@dynamic.route('/delete_comment')
def delete_comment():
    try:
        comment = Comment.query.filter(Comment.id == request.args.get("id")).first()
        db.session.delete(comment)
        db.session.commit()
        return json.dumps({'code': 1})
    except:
        return json.dumps({'code': -1})


@dynamic.route('/check_dynamic_comment')
def check_dynamic_comment():
    try:
        comment = Comment.query.filter(Comment.id == request.args.get('comment_id')).first()
        comment.checked = True
        db.session.commit()
        return json.dumps({'code': 1})
    except:
        return json.dumps({'code': -1})


@dynamic.route('/add_dynamic', methods=['POST'])
def add_dynamic():
    try:
        data = json.loads(request.data.decode())
        dynamic_type = data["dynamic_type"]
        id = str(uuid.uuid1())
        if dynamic_type == '0':
            dynamic = Dynamics(None, session["user_number"], session["user_type"], data["content"], '')
        else:
            stu = Student.query.filter_by(number=session["user_number"]).first()
            dynamic = Dynamics(stu.classes.id, session["user_number"], session["user_type"], data["content"], '')
        dynamic.id = id
        dynamic.type = dynamic_type
        db.session.add(dynamic)
        db.session.commit()
        return json.dumps({'code': 1, 'id': id})
    except:
        return json.dumps({'code': -1})


@dynamic.route("/upload_dynamic_image", methods=["POST"])
def upload_dynamic_image():
    path = os.path.abspath(os.path.join(os.getcwd(), './app/upload/dynamic/images/'))
    if not os.path.exists(path):
        os.makedirs(path)
    try:
        file = request.files["file"]
        file_name = str(uuid.uuid1()) + "." + file.filename.split(".")[-1:][0]
        save_path = path + "/" + file_name
        file.save(save_path)
        img = Image.open(save_path)
        height = img.size[1]
        width = img.size[0]
        img.thumbnail((width // 1.5, height // 1.5))
        img.save(save_path)
        id = request.form["id"]
        dynamic = Dynamics.query.filter(Dynamics.id == id).first()
        dynamic.imges += ("#" + file_name)
        dynamic.imges = dynamic.imges.strip('#')
        db.session.commit()
        return json.dumps({"code": 1})
    except:
        return json.dumps({"code": -1})


@dynamic.route('/get_my_dynamic')
def get_my_dynamic():
    cur_page = int(request.args.get("page"))
    pagination = Dynamics.query.filter(Dynamics.publisher_number == session['user_number']).order_by(
        db.desc(Dynamics.add_time)).paginate(cur_page, 20, False)
    has_next_page = (False if pagination.page == pagination.pages else True)
    data = format_dynamic(pagination.items)
    return json.dumps({"has_next_page": has_next_page, "data": data})


@dynamic.route('/get_user_dynamic')
def get_user_dynamic():
    cur_page = int(request.args.get("page"))
    pagination = Dynamics.query.filter(Dynamics.publisher_number == request.args.get("user_number")).order_by(
        db.desc(Dynamics.add_time)).paginate(cur_page, 20, False)
    has_next_page = (False if pagination.page == pagination.pages else True)
    data = format_dynamic(pagination.items)
    return json.dumps({"has_next_page": has_next_page, "data": data})


@dynamic.route('/delete_dynamic')
def delete_dynamic():
    try:
        dynamic = Dynamics.query.filter(Dynamics.id == request.args.get('id')).first()
        if dynamic.imges or dynamic.imges == '':
            try:
                imgs = dynamic.imges.split("#")
                for i in imgs:
                    os.remove('app/upload/dynamic/images/' + i)
            except:
                pass
        db.session.delete(dynamic)
        db.session.commit()
        return json.dumps({'code': 1})
    except:
        return json.dumps({"code": -1})


@dynamic.route('/get_class_dynamic')
def get_class_dynamic():
    user_class_id = Student.query.filter(Student.number == session["user_number"]).first().classes.id
    cur_page = int(request.args.get("page"))
    pagination = Dynamics.query.filter(Dynamics.classes_id == user_class_id, Dynamics.type == '1').order_by(
        db.desc(Dynamics.add_time)).paginate(cur_page, 20, False)
    has_next_page = (False if pagination.page == pagination.pages else True)
    data = format_dynamic(pagination.items)
    return json.dumps({"has_next_page": has_next_page, "data": data})


if __name__ == "__main__":
    get_news_content()
