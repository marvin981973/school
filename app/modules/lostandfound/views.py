import json
import uuid
import os

from PIL import Image
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
    search_text = request.args.get("search_text", "")
    if (search_text == ""):
        pagination = LostFound.query.filter(LostFound.status == '0').order_by(db.desc(LostFound.add_time)).paginate(
            cur_page, 10, False)
    else:
        pagination = LostFound.query.filter(LostFound.status == '0',
                                            LostFound.lost_object.like("%" + search_text + "%")).order_by(
            db.desc(LostFound.add_time)).paginate(
            cur_page, 10, False)
    has_next_page = (False if pagination.page == pagination.pages else True)
    data = []
    for item in pagination.items:
        data.append({
            "add_time": item.add_time.strftime("%Y-%m-%d %H:%M:%S"),
            "publisher_name": item.publisher_name,
            "place": item.place,
            "lost_object": item.lost_object,
            "img_url": item.img_url if item.img_url else 'default.jpg',
            "phone": item.telephone,
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
            "add_time": item.add_time.strftime("%Y-%m-%d %H:%M:%S"),
            "publisher_name": item.publisher_name,
            "id": item.id,
            "place": item.place,
            "lost_object": item.lost_object,
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
        try:
            os.remove('app/upload/lostandfound/images/' + lost.img_url)
        except:
            pass
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
    save_path = path + "/" + file_name
    file.save(save_path)
    img = Image.open(save_path)
    height = img.size[1]
    width = img.size[0]
    img.thumbnail((width // 1.5, height // 1.5))
    img.save(save_path)

    return json.dumps({"code": 1, "file_name": file_name})


@lostandfound.route("/add_lost", methods=["POST"])
def add_lost():
    data = json.loads(request.data.decode())
    publisher = session["user_number"]
    publisher_name = Student.query.filter(Student.number == publisher).first().name if session[
                                                                                           "user_type"] == 's' else Teacher.query.filter(
        Teacher.number == publisher).first().name
    lost = LostFound(publisher, publisher_name, data['lost_object'], data["place"], data["description"],
                     data["img_url"], data["telephone"])
    lost.id = str(uuid.uuid1())
    db.session.add(lost)
    db.session.commit()
    return json.dumps({"code": 1})


if __name__ == "__main__":
    print(os.path.abspath(os.path.join(os.getcwd(), "..\..", './upload/lostandfound/images/')))
