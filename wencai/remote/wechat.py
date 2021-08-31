import click
import requests
from wencai.util.utils import ech
import base64, hashlib


global_key = '0b7f6837-2f8d-485c-821a-5ba26215e92e'
def send_url(debug=False):
    if debug:
        return send_url() + '&debug=1'
    return f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={global_key}'


def upload_url(debug=False):
    if debug:
        return upload_url() + '&debug=1'
    return f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={global_key}&type=file"

"""
curl 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0b7f6837-2f8d-485c-821a-5ba26215e92e' \
   -H 'Content-Type: application/json' \
   -d '
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
    }'
"""
def send_news(title, description, picurl):
    requests.post(
        url=send_url(), 
        headers={"Content-Type": "news"},
        news={"articles": [
                {"title": title, "description": description, "url": send_url(), "picurl": picurl}
            ]}
    )


def send_pic(pic):
    with open(pic, 'rb') as f:
        base64_data = base64.b64encode(f.read())
        base64_data = base64_data.decode()
    with open(pic, 'rb') as f:
        fmd5 = hashlib.md5(f.read()).hexdigest()
    requests.post(
        url=send_url(), 
        headers={"Content-Type": "image"}, 
        json={"msgtype": "image", "image": {"base64": base64_data, "md5": fmd5}}
    )


"""
curl 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0b7f6837-2f8d-485c-821a-5ba26215e92e' \
   -H 'Content-Type: application/json' \
   -d '
    {
        "msgtype": "markdown",
        "markdown": {
            "content": "实时新增用户反馈<font color=\"warning\">132例</font>，请相关同事注意。\n
            >类型:<font color=\"comment\">用户反馈</font>
            >普通用户反馈:<font color=\"comment\">117例</font>
            >VIP用户反馈:<font color=\"comment\">15例</font>"
        }
    }'
"""
# 不能使用data,data的数据只能是字典，列表或者元组。而json= 发送的是json的数据，所以这里需要使用json
def send_md(content):
    requests.post(
        url=send_url(), 
        headers={"Content-Type": "application/json"}, 
        json= {"msgtype": "markdown", "markdown": {
                "content": content
            }
        }
    )


"""
https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key=KEY&type=file
{
    "msgtype": "file",
    "file": {
         "media_id": "3a8asd892asd8asd"
    }
}
"""
def post_file_to_wechat(filepath):
    from requests_toolbelt import MultipartEncoder
    filename = filepath.split('/')[-1]
    m = MultipartEncoder(fields={filename: ('file', open(filepath, 'rb'), 'text/plain')})   # 'application/octet-stream'
    print(m)
    r = requests.post(url=upload_url(), data=m, headers={'Content-Type': m.content_type, 'filename': filename})
    output = r.json()
    return output['media_id']


def post_file(filepath):
    filename = filepath.split('/')[-1]
    files = {
        'filename': filename,
        filename: (filename, open(filepath, 'rb'), 'application/octet-stream')
    }
    r = requests.post(upload_url(), files=files)
    output = r.json()
    return output['media_id']



def send_file(filepath):
    media_id = post_file(filepath)
    ech("your media_id is: %s" % click.style(media_id, 'blue'))
    requests.post(
        url=send_url(),
        headers={"Content-Type": "application/json"}, 
        json= {"msgtype": "file", "file": {
                "media_id": media_id
            }
        }
    )


"""
curl 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0b7f6837-2f8d-485c-821a-5ba26215e92e' \
   -H 'Content-Type: application/json' \
   -d '
    {
        "msgtype": "text",
        "text": {
            "content": "广州今日天气：29度，大部分多云，降雨概率：60%",
            # "mentioned_list":["wangqing","@all"],
            "mentioned_mobile_list":["13800001111","@all"]
        }
    }'
"""
def send_text(content):
    response = requests.post(
        url=send_url(), 
        headers={"Content-Type": "application/json"},
        json={"msgtype": "text", "text": {
                "content": content
            }
        }
    )
    response = response.json()
    print(response)


if __name__ == "__main__":
    # send_text('hello!')
    send_file('wechat.py')
