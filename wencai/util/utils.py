import binascii
import sys
from pyDes import des, triple_des, CBC, PAD_PKCS5
import os
import requests
import click
from selenium import webdriver
import requests
import re
import subprocess
import time
import os
import platform
from datetime import datetime
import pickle


def check_output(_CMD):
    return subprocess.check_output(_CMD).decode("utf-8", "ignore").replace("\"", "").strip()


def get_system():
    system = platform.system()
    if system == 'Linux':
        if check_output(['cat', '/etc/issue']).count('Ubuntu'):
            return 'Ubuntu'
        return 'CentOS'
    return system


def get_tmp_path():
    tmp_path = '/tmp'
    if get_system() == 'Windows':
        # C:/Users/Sunie/AppData/Local/Temp
        tmp_path = os.environ['TEMP'].replace(r'\\', '/').replace('\\', '/')
    return tmp_path + '/wencai'


driver_path = f'{get_tmp_path()}/chromedriver'


def now(pattern="%Y-%m-%dt%H:%M:%S"):
    return datetime.now().strftime(pattern)


if os.path.exists('/sys/class/net/eth0/address'):
    KEY = check_output(['cat', '/sys/class/net/eth0/address']) * 2
else:
    KEY = 'qwertyuiopasdfghjklzxcvbnm'


def ech(s, color=None):
    click.echo(click.style(s, fg=color))


def init_option(disableGPU=True, imagesDisabled=True, headless=True):
    options = webdriver.ChromeOptions()
    if disableGPU:
        options.add_argument('--disable-gpu')
    # 隐藏滚动条, 应对一些特殊页面
    options.add_argument('--hide-scrollbars')
    # 不加载图片, 提升速度
    if imagesDisabled:
        options.add_argument('blink-settings=imagesEnabled=false')
    # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    if headless:
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
        # 匹配文件夹（版本号）和时间，这里一定要最小匹配
        result = re.compile(version + r'\..*?/').findall(rep)[0]

    if platform.system() == "Linux":
        download_url = url + result + 'chromedriver_linux64.zip'
    else:
        download_url = url + result + 'chromedriver_mac64.zip'
    ech("downloading %s" % (click.style(download_url, 'blue')))
    file = requests.get(download_url)
    with open(f"{driver_path}.zip", 'wb') as zip_file:                # 保存文件到脚本所在目录
        zip_file.write(file.content)
    time.sleep(1)
    subprocess.Popen(
        ['unzip', '-o', f'{driver_path}.zip', '-d', os.path.dirname(driver_path)])
    time.sleep(1)
    os.system(f'chmod 777 {driver_path}')
    ech(f"successfully saved at {driver_path}", 'green')


def init_driver():
    if not os.path.exists(driver_path):
        download_webdriver()
    # os.environ['PATH'] = os.environ['PATH'] + ':/tmp/remote'
    driver = webdriver.Chrome(options=init_option(),
                              executable_path=driver_path)
    return driver


def get_secret_key(secret_key):
    if secret_key is None:
        return KEY[:24]
    else:
        while len(secret_key) < 24:
            secret_key = secret_key * 2
        return secret_key[:24]


def des_encrypt(s, secret_key=None):
    secret_key = get_secret_key(secret_key)
    iv = secret_key[-8:]
    k = triple_des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(s, padmode=PAD_PKCS5)
    return 'encrypted#' + binascii.b2a_hex(en).decode(encoding='utf-8')


def des_decrypt(s, secret_key=None):
    assert(s.startswith('encrypted#'))
    s = s[10:]
    secret_key = get_secret_key(secret_key)
    iv = secret_key[-8:]
    k = triple_des(secret_key, mode=CBC, IV=iv, padmode=PAD_PKCS5)
    de = k.decrypt(binascii.a2b_hex(s), padmode=PAD_PKCS5)
    return de.decode(encoding='utf-8')


def dropun(X):
    for x in X.columns:
        if x[:7] == 'Unnamed':
            X = X.drop(columns=[x])
    return X


def has_alpha(s):
    for c in s:
        if 'A' <= c <= 'Z' or 'a' <= c <= 'z':
            return True
    return False


def pre_process(s):
    lines = s.split('\n')
    s = ''
    i = 0
    while i < len(lines):
        if has_alpha(lines[i]):
            line = lines[i].strip()
            s += line
            if line[-1] in [',', ';']:
                s += ' '
            elif line[-1] == '.':
                s += '\n'
            else:
                s += ' '
        i += 1
    if len(s) > 1000:
        return s
    return None


def convertPdf2Txt():
    path = 'core_qmof_pdf/'
    dest = 'core_qmof_txt/'
    if not os.path.exists(dest):
        os.mkdir(dest)

    for pdf in os.listdir(path):
        name = pdf[:-4] + '.txt'
        s = path + pdf
        d = dest + name
        if os.path.exists(d):
            continue
        try:
            s = Pdf2Txt(s)
            s = pre_process(s)
            with open(d, 'w', encoding='utf-8') as f:
                f.write(s)
        except:
            print(pdf, 'failed')


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def find_continuous_num(astr, c):
    num = ''
    try:
        while not is_number(astr[c]) and c < len(astr):
            c += 1
        while is_number(astr[c]) and c < len(astr):
            num += astr[c]
            c += 1
    except:
        pass
    if num != '':
        return int(num)


def comp2filename(file1, file2):
    smaller_length = min(len(file1), len(file2))
    continuous_num = ''
    for c in range(0, smaller_length):
        if not is_number(file1[c]) and not is_number(file2[c]):
            # print('both not number')
            if file1[c] < file2[c]:
                return True
            if file1[c] > file2[c]:
                return False
            if file1[c] == file2[c]:
                if c == smaller_length - 1:
                    # print('the last bit')
                    if len(file1) < len(file2):
                        return True
                    else:
                        return False
                else:
                    continue
        if is_number(file1[c]) and not is_number(file2[c]):
            return True
        if not is_number(file1[c]) and is_number(file2[c]):
            return False
        if is_number(file1[c]) and is_number(file2[c]):
            if find_continuous_num(file1, c) < find_continuous_num(file2, c):
                return True
            else:
                return False


def sort_insert(lst):
    for i in range(1, len(lst)):
        x = lst[i]
        j = i
        while j > 0 and lst[j-1] > x:
            # while j > 0 and comp2filename(x, lst[j-1]):
            lst[j] = lst[j-1]
            j -= 1
        lst[j] = x
    return lst


def sort_filename(lst):
    for i in range(1, len(lst)):
        x = lst[i]
        j = i
        # while j > 0 and lst[j-1] > x:
        while j > 0 and comp2filename(x, lst[j-1]):
            lst[j] = lst[j-1]
            j -= 1
        lst[j] = x
    return lst


def init_OCR():
    import pytesseract

    # your path may be different
    pytesseract.pytesseract.tesseract_cmd = f'{get_tmp_path()}/tesseract.exe'


def save_obj(obj, name):
    with open(name, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open(name, 'rb') as f:
        return pickle.load(f)


def getPureDomainCookies(cookies):
    domain2cookie = {}  # 做一个域到cookie的映射
    for cookie in cookies:
        domain = cookie['domain']
        if domain in domain2cookie:
            domain2cookie[domain].append(cookie)
        else:
            domain2cookie[domain] = []
    maxCnt = 0
    ansDomain = ''
    for domain in domain2cookie.keys():
        cnt = len(domain2cookie[domain])
        if cnt > maxCnt:
            maxCnt = cnt
            ansDomain = domain
    ech('your pure domain cookies are:', 'yellow')
    ech(domain2cookie)
    ansCookies = domain2cookie[ansDomain]
    return ansCookies


def timewrap(func, **kwargs):
    s = datetime.datetime.now()
    func(**kwargs)
    print('时间=', (datetime.datetime.now() - s).seconds)


def verification_OCR(pic_path, count=None):
    '''识别图片中的code，count表示验证码位数，默认任意长
    apt update
    apt install -y python3-pil  tesseract-ocr
    pip install pytesseract tesseract
    '''
    import pytesseract
    from PIL import Image, ImageEnhance
    img = Image.open(pic_path)

    times = 0
    code = ''
    while True:
        times += 1
        ech(times)
        code = pytesseract.image_to_string(img).strip().replace(' ', '')
        if len(code) and count is None or len(code) == count:
            break

    ech("输出的验证码为：%s" % click.style(code, 'blue'))
    return code


if __name__ == "__main__":
    # print(get_newest_version('sunie'))
    # print(verification_OCR('/tmp/remote/test.png', 6))
    print(verification_OCR('/tmp/wencai/tmp.png'))
