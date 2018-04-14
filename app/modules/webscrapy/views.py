from app.modules.webscrapy import webscrapy
import json
from flask import request
from lxml import etree
from app.tools.WebPageParsing import ScrapyPage


@webscrapy.route('/get_news_list', methods=['POST'])
def get_news_list():
    content = json.loads(request.data.decode())
    static_url = 'http://jwc.ahut.edu.cn/list.jsp'

    html = ScrapyPage(static_url + content['nextPageUrl'])
    selector = etree.HTML(html)
    news = selector.xpath("//a[@class='c44456']")
    try:
        next_page = selector.xpath("//a[@class='Next']/@href")[0]
    except IndexError:
        next_page = '-1'

    res = []
    for new in news:
        data = {
            "href": new.xpath("./@href")[0],
            "title": new.xpath("./text()")[0].strip(),
            "time": new.xpath("../following-sibling::td[1]/text()")[0][1:-2]
        }
        res.append(data)
    return json.dumps({"news": res, 'nextPageUrl': next_page})


@webscrapy.route('/get_news_content', methods=['POST'])
def get_news_content():
    content_url = json.loads(request.data.decode())["contentUrl"]
    static_url = 'http://jwc.ahut.edu.cn'
    html = ScrapyPage(static_url + "/" + content_url)
    selector = etree.HTML(html)
    content = str(selector.xpath("//div[@id='vsb_content']")[0].xpath("string(.)")).strip()
    # content='\n'.join(content.split())
    return json.dumps({'content': content})
