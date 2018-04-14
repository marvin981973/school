from app.modules.public import public

import json

from flask import Response, request, session

from app.modules.weather.weather import Weather

from app.config import wx_config

from app.tools.WebPageParsing import ScrapyPage
from app.models import UserBind, SchoolScenery


@public.route('/')
def hello():
    return "Hello World"


@public.route('/image/<image_id>')
def get_image(image_id):
    image = open('app/static/images/{}'.format(image_id), 'rb')
    return Response(image, mimetype='image/jpeg')


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
        session['open_id'] = open_id
        return UserBind.check_bind(open_id)
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


@public.route('/get_user_type')
def get_user_type():
    return json.dumps({"user_type": session["user_type"]})


@public.route('/get_weather')
def get_weather():
    city_code = request.args.get('city_code')
    res = Weather.get_weather(city_code)
    return res


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
