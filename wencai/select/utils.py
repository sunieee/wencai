import requests
import json
import collections
import click
import selenium
from selenium import webdriver
import requests
import re
import subprocess
import time
import os
import platform
import base64
import hashlib


driver_path = '/tmp/wencai/chromedriver'


def ech(s, color=None):
    click.echo(click.style(s, fg=color))


def check_output(_CMD):
    return subprocess.check_output(_CMD).decode("utf-8", "ignore").replace("\"", "").strip()


def init_option():
    options = webdriver.ChromeOptions()
    # options.add_argument('--disable-gpu')
    # 隐藏滚动条, 应对一些特殊页面
    options.add_argument('--hide-scrollbars')
    # 不加载图片, 提升速度
    options.add_argument('blink-settings=imagesEnabled=false')
    # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    options.add_argument('--headless')
    # 以最高权限运行
    options.add_argument('--no-sandbox')
    # 禁用JavaScript
    options.add_argument("--disable-javascript")
    return options


def download_webdriver():
    # 获取版本号（去除小数点后）
    url = 'http://npm.taobao.org/mirrors/chromedriver/'
    out = check_output(['google-chrome', '--version'])
    out = out.split()[-1]
    version = '.'.join(out.split('.')[:-1])
    ech('your google version is: %s' % click.style(out, 'green'))
    rep = requests.get(url).text

    if len(re.compile(out).findall(rep)) > 0:
        result = re.compile(out).findall(rep)[0]
    else:
        result = re.compile(version + r'\..*?/').findall(rep)[0]  # 匹配文件夹（版本号）和时间，这里一定要最小匹配

    if platform.system() == "Linux":
        download_url = url + result + 'chromedriver_linux64.zip'
    else:
        download_url = url + result + 'chromedriver_mac64.zip'
    ech("downloading %s" % (click.style(download_url, 'blue')))
    file = requests.get(download_url)
    with open(f"{driver_path}.zip", 'wb') as zip_file:                # 保存文件到脚本所在目录
        zip_file.write(file.content)
    time.sleep(1)
    subprocess.Popen(['unzip', '-o', f'{driver_path}.zip', '-d', os.path.dirname(driver_path)])
    time.sleep(1)
    os.system(f'chmod 777 {driver_path}')
    ech(f"successfully saved at {driver_path}", 'green')


def init_driver():
    if not os.path.exists(driver_path):
        download_webdriver()
    # os.environ['PATH'] = os.environ['PATH'] + ':/tmp/remote'
    driver = webdriver.Chrome(options=init_option(), executable_path=driver_path)
    return driver


def get_newest_version(branch):
    # http://spring.sensetime.com/pypi/dev/packages/
    # spring_aux-???-py3-none-any.whl
    url = 'http://sunie.tpddns.cn:9007/packages/'
    rep = requests.get(url).text
    ans = ''
    for line in rep.split('\n'):
        if line.count('wencai'):
            if line.count(branch):
                ans = line
    return ans.split('"')[1].split('-')[1]


def send_pic(pic, url='https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0b7f6837-2f8d-485c-821a-5ba26215e92e'):
    headers = {"Content-Type": "text/plain"}
    with open(pic, 'rb') as f:
        base64_data = base64.b64encode(f.read())
        base64_data = base64_data.decode()
    with open(pic, 'rb') as f:
        fmd5 = hashlib.md5(f.read()).hexdigest()
    data = {"msgtype": "image", "image": {"base64": base64_data, "md5": fmd5}}
    requests.post(url=url, headers=headers, json=data)
