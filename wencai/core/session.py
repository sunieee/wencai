# -*- coding:utf-8 -*-
import requests
from wencai.core.cookies import WencaiCookie


class Session(requests.Session):
    headers = {
        "Accept": "application/json,text/javascript,*/*;q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8",
        'Connection': 'keep-alive',
        'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
        'X-Requested-With': "XMLHttpRequest"

    }

    def __init__(self):
        requests.Session.__init__(self)
        self.headers.update(Session.headers)

    def update_headers(self, source, add_headers):
        self.headers['hexin-v'] = WencaiCookie().getHexinVByJson(source=source)
        if add_headers is not None:
            if not isinstance(add_headers, dict):
                raise TypeError('update_headers should be `dict` type.')
            for k, v in add_headers.items():
                self.headers[k] = v

    def get_result(self, url, source, add_headers=None, **kwargs):
        self.update_headers(add_headers=add_headers, source=source)
        return super(Session, self).get(url=url, **kwargs)

    def post_result(self, url, source, data=None, json=None, add_headers=None, **kwargs):
        self.update_headers(add_headers=add_headers, source=source)
        return super(Session, self).post(url=url, data=data, json=json, **kwargs)
