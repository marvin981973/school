import json
import uuid
import os

from flask import request, Response, session

from app import db
from app.models import LostFound, Teacher, Student
from app.modules.lostandfound import lostandfound


@lostandfound.route("/")
def say_hello():
    return "this is the lostandfound page"


@lostandfound.route("/images/<image_id>")
def load_images(image_id):
    try:
        image = open('app/upload/lostandfound/images/{}'.format(image_id), 'rb')
    except:
        image = open('app/upload/lostandfound/images/default.jpg', 'rb')
    return Response(image, mimetype='image/jpeg')


@lostandfound.route("/load_list")
def load_list():
    cur_page = int(request.args.get("page"))
    pagination = LostFound.query.filter(LostFound.status == '0').order_by(db.desc(LostFound.add_time)).paginate(
        cur_page, 10, False)
    has_next_page = (False if pagination.page == pagination.pages else True)
    data = []
    for item in pagination.items:
        data.append({
            "add_time": item.add_time.strftime("%Y-%m-%d"),
            "publisher_name": item.publisher_name,
            "title": item.title,
            "img_url": item.img_url if item.img_url else 'default.jpg',
            "description": item.description
        })
    return json.dumps({"has_next_page": has_next_page, "data": data})


@lostandfound.route("/load_mylost")
def load_mylost():
    items = LostFound.query.filter(LostFound.publisher == session["user_number"]).order_by(
        db.desc(LostFound.add_time)).all()
    data = []
    for item in items:
        data.append({
            "add_time": item.add_time.strftime("%Y-%m-%d"),
            "publisher_name": item.publisher_name,
            "id": item.id,
            "title": item.title,
            "img_url": item.img_url if item.img_url else 'default.jpg',
            "description": item.description,
            "status": item.status
        })
    return json.dumps({"data": data})


@lostandfound.route("/delete_lost")
def delete_lost():
    id = request.args.get("id")
    lost = LostFound.query.filter(LostFound.id == id).first()
    if lost.img_url != "default.jpg":
        os.remove('app/upload/lostandfound/images/' + lost.img_url)
    db.session.delete(lost)
    db.session.commit()
    return json.dumps({"code": 1})


@lostandfound.route("/modify_lost")
def modify_lost():
    id = request.args.get("id")
    option = request.args.get("option")
    lost = LostFound.query.filter(LostFound.id == id).first()
    lost.status = option
    db.session.add(lost)
    db.session.commit()
    return json.dumps({"code": 1})


@lostandfound.route("/upload", methods=["POST"])
def upload():
    path = os.path.abspath(os.path.join(os.getcwd(), './app/upload/lostandfound/images/'))
    if not os.path.exists(path):
        os.makedirs(path)
    file = request.files["file"]
    file_name = str(uuid.uuid1()) + "." + file.filename.split(".")[-1:][0]
    file.save(path + "/" + file_name)
    return json.dumps({"code": 1, "file_name": file_name})


@lostandfound.route("/add_lost", methods=["POST"])
def add_lost():
    data = json.loads(request.data.decode())
    publisher = session["user_number"]
    publisher_name = Student.query.filter(Student.number == publisher).first().name if session[
                                                                                           "user_type"] == 's' else Teacher.query.filter(
        Teacher.number == publisher).first().name
    lost = LostFound(publisher, publisher_name, data["title"], data["description"], data["img_url"])
    db.session.add(lost)
    db.session.commit()
    return json.dumps({"code": 1})


if __name__ == "__main__":
    print(os.path.abspath(os.path.join(os.getcwd(), "..\..", './upload/lostandfound/images/')))
