import json

from app.modules.library import library
from flask import request, Response
from app.tools.WebPageParsing import ScrapyPage
from lxml import etree
import urllib


@library.route('/')
def say_hello():
    return 'this is the library page'


@library.route('/search_books')
def search_books():
    static_url = 'http://10.100.101.10:8080/opac/openlink.php?historyCount=0&doctype=ALL&match_flag=forward&displaypg=20&sort=CATA_DATE&orderby=desc&showmode=list&dept=ALL'
    search_string = request.args.get('strText')
    search_type = request.args.get('strSearchType')
    static_url += ("&strText=" + search_string + "&strSearchType=" + search_type)
    selector = etree.HTML(ScrapyPage(static_url))
    return json.dumps(get_books(selector))


@library.route('/search_next_page', methods=['POST'])
def search_next_page():
    static_url = 'http://10.100.101.10:8080/opac/openlink.php'
    static_url += json.loads(request.data.decode())["next_page"]
    selector = etree.HTML(ScrapyPage(static_url))
    return json.dumps(get_books(selector))


@library.route('/get_book_detail')
def get_book_detail():
    static_url = 'http://10.100.101.10:8080/opac/item.php'
    book_id = request.args.get("book_id")
    static_url += ("?marc_no=" + book_id)
    selector = etree.HTML(ScrapyPage(static_url))
    dls = selector.xpath("//div[@id='item_detail']/dl")[:-2]
    res = []
    for dl in dls:
        title = dl.xpath("./dt/text()")[0]
        content = dl.xpath("./dd")[0].xpath("string(.)")
        if 'ISBN' in title:
            isbn = content.split('/')[0].replace('-', '')
        res.append({
            'title': title,
            'content': content
        })

    borrow = selector.xpath("//table[@id='item']/tr")[1:]
    borrow_info = []
    for borrow_ in borrow:
        td = borrow_.xpath("./td")
        try:
            borrow_info.append({
                'index': td[0].xpath("./text()")[0],
                'tiao_ma': td[1].xpath("./text()")[0],
                'xiao_qu': td[3].xpath("./text()")[0].strip(),
                'status': td[4].xpath("string(.)")
            })
        except IndexError as e:
            continue
    return json.dumps({
        'info': res,
        'book_img': json.loads(ScrapyPage('http://10.100.101.10:8080/opac/ajax_douban.php?isbn=' + isbn))['image'],
        'borrow_info': borrow_info
    })


@library.route('/get_book_img/<book_img>')
def get_book_img(book_img):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'Upgrade-Insecure-Requests': '1'
    }
    req = urllib.request.Request('http://img7.doubanio.com/view/subject/s/public/' + book_img, headers=header)
    try:
        return Response(urllib.request.urlopen(req).read(), mimetype='image/jpeg')
    except urllib.error.HTTPError as e:
        return Response(open('app/static/images/nobook.jpg', 'rb'), mimetype='image/jpeg')


def get_books(selector):
    books_li = selector.xpath("//li[@class='book_list_info']")
    books = []
    for book_li in books_li:
        book_store = book_li.xpath('./p/span/text()')
        book_info = book_li.xpath('./p/text()')
        book = {
            'book_index': book_li.xpath('./h3/text()')[0].strip(),
            'book_name': book_li.xpath('./h3/a')[0].xpath('string(.)'),
            'book_language_type': book_li.xpath('./h3/span/text()')[0][:2],
            'book_store_info': book_store[0],
            'book_borrow_info': book_store[1].strip(),
            'book_author': book_info[1],
            'book_press': book_info[2].strip(),
            'book_id': book_li.xpath('./p/a/@href')[0].split('=')[1]
        }
        books.append(book)

    pagination_info = selector.xpath("//span[@class='pagination']/a")
    next_page = 0
    next_page_url = ''
    if len(pagination_info) == 2:
        next_page = 1
        next_page_url = pagination_info[1].xpath("./@href")[0]

    sd = selector.xpath("//span[@class='pagination']/text()")
    if len(pagination_info) == 1:
        if "上一页" in selector.xpath("//span[@class='pagination']/text()")[0]:
            next_page = 1
            next_page_url = pagination_info[0].xpath("./@href")[0]

        else:
            next_page = 0

    res = {
        "books": books,
        "next_page": next_page,
        "next_page_url": next_page_url
    }
    return res
