from app import db
from app.models import SchoolDynamic, Student, Teacher
from app.modules.dynamic import dynamic
import json
from flask import request
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


@dynamic.route('/get_school_dynamic')
def get_school_dynamic():
    cur_page = int(request.args.get("page"))
    pagination = SchoolDynamic.query.order_by(db.desc(SchoolDynamic.add_time)).paginate(cur_page, 20, False)
    has_next_page = (False if pagination.page == pagination.pages else True)
    data = []
    for item in pagination.items:
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
        data.append({
            "id": item.id,
            "time": item.add_time.strftime("%Y-%m-%d %H:%M:%S"),
            "content": item.content,
            "heart_count": item.heart_count,
            "publisher_number": item.publisher_number,
            "publisher_name": user.name,
            "head_url": user.head_url,
            "content": item.content,
            "have_img": length,
            "images": images
        })
    return json.dumps({"has_next_page": has_next_page, "data": data})

    if __name__ == "__main__":
        get_news_content()
