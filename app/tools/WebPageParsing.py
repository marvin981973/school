from urllib import request as ur
from urllib.parse import quote
import string


def ScrapyPage(url):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }
    punctuation = r"""!"%&'()*,-./:;<=>?[\]^_`{|}~"""
    printable = string.digits + string.ascii_letters + punctuation + string.whitespace
    url = quote(url, safe=printable)
    request = ur.Request(url, headers=header)
    html = ur.urlopen(request).read().decode(encoding='utf-8')
    return html
