import binascii
from pyDes import triple_des, CBC, PAD_PKCS5
import os
import requests
import click
from selenium import webdriver
import requests, re, subprocess, time
import os, platform
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import *
from pdfminer.converter import PDFPageAggregator


driver_path = '/tmp/wencai/chromedriver'

def check_output(_CMD):
    return subprocess.check_output(_CMD).decode("utf-8", "ignore").replace("\"", "").strip()

if os.path.exists('/sys/class/net/eth0/address'):
    KEY = check_output(['cat', '/sys/class/net/eth0/address']) * 2
else:
    KEY = 'qwertyuiopasdfghjklzxcvbnm'


def ech(s, color=None):
    click.echo(click.style(s, fg=color))


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
        if line.count('wencai') and line.count('.whl'):
            if line.count(branch):
                ans = line
    return ans.split('"')[1].split('-')[1]


def get_secret_key(secret_key):
    if secret_key is None:
        return  KEY[:24]
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


def Pdf2Txt(pdf_path):
    fp = open(pdf_path,'rb')
    s = ''
    # 来创建一个pdf文档分析器
    parser = PDFParser(fp)
    # 创建一个PDF文档对象存储文档结构
    document = PDFDocument(parser)
    # 检查文件是否允许文本提取
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    else:
        # 创建一个PDF资源管理器对象来存储共赏资源
        rsrcmgr = PDFResourceManager()
        # 设定参数进行分析
        laparams = LAParams()
        # 创建一个PDF设备对象
        # device=PDFDevice(rsrcmgr)
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        # 创建一个PDF解释器对象
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        # 处理每一页
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            # 接受该页面的LTPage对象
            layout = device.get_result()
            for x in layout:
                if(isinstance(x, LTTextBoxHorizontal)):
                    s += x.get_text()
    return s


def dropun(X):
    for x in X.columns:
        if x[:7]=='Unnamed':
              X=X.drop(columns=[x])
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


if __name__ == "__main__":
    print(get_newest_version('sunie'))
