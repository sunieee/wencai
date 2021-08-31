import click
import os, requests
from wencai.util.utils import ech
from wencai import __version__


filepath = os.path.dirname(os.path.abspath(__file__))  # 1. 源文件夹
src_path = os.path.dirname(filepath)   # 上一个文件夹


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


def upload():
    os.system(f'sh {filepath}/upload.sh')


def update():
    branch = 'sunie'
    """update wencai to the newest version"""
    ech('on branch: %s' % click.style(branch, 'blue'))
    version = get_newest_version(branch)
    ech('the newest version is: %s' % click.style(version, 'blue'))
    os.system("pip install http://sunie.tpddns.cn:9007/packages/" + f"wencai-{version}-py3-none-any.whl  --user --upgrade")
    ech(f'successfully update wencai({version})', 'green')


def version():
    ech(__version__, 'green')