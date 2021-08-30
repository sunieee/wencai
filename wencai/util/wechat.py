import requests, base64, hashlib

global_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0b7f6837-2f8d-485c-821a-5ba26215e92e'
global_key = '0b7f6837-2f8d-485c-821a-5ba26215e92e'

"""
{
    "msgtype": "news",
    "news": {
       "articles" : [
           {
               "title" : "中秋节礼品领取",
               "description" : "今年中秋节公司有豪礼相送",
               "url" : "www.qq.com",
               "picurl" : "http://res.mail.qq.com/node/ww/wwopenmng/images/independent/doc/test_pic_msg1.png"
           }
        ]
    }
}
"""


def send_news(title, description, picurl, url=global_url):
    requests.post(url=url, headers={"Content-Type": "news"},
        news={"articles": [
                {"title": title, "description": description, "url": url, "picurl": picurl}
            ]}
    )


def send_pic(pic, url=global_url):
    with open(pic, 'rb') as f:
        base64_data = base64.b64encode(f.read())
        base64_data = base64_data.decode()
    with open(pic, 'rb') as f:
        fmd5 = hashlib.md5(f.read()).hexdigest()
    requests.post(url=url, headers={"Content-Type": "image"}, 
        json={"msgtype": "image", "image": {"base64": base64_data, "md5": fmd5}}
    )


def send_md(content, url=global_url):
    requests.post(url=url, headers={"Content-Type": "application/json"}, 
        data= {"msgtype": "markdown", "markdown": content}
    )


def send_file(path, url=global_url):
    """
    https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key=KEY&type=file
    """ 
    pass