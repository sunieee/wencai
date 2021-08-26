import click
import os
from wencai import __version__
from wencai.select.utils import get_newest_version, ech
from wencai.core.crawler import Wencai

wc = Wencai(cn_col=True)

@click.command()
def version():
    print(__version__)


@click.group()
def cli():
    pass


@click.command()
@click.option('-b', '--branch', default='sunie', help="spring branch to update")
def update(branch):
    """update wencai to the newest version(default branch: develop)"""
    ech('on branch: %s' % click.style(branch, 'blue'))
    version = get_newest_version(branch)
    ech('the newest version is: %s' % click.style(version, 'blue'))
    os.system("pip install http://sunie.tpddns.cn:9007/packages/" + f"wencai-{version}-py3-none-any.whl  --user --upgrade")
    ech(f'successfully update spring.submit({version})', 'green')


@click.command()
@click.argument('conditions', nargs=-1)
def search(conditions):
    """ser"""
    s0 = '，'.join(conditions)
    if len(conditions) == 0:
        s0 = '连续5年ROE大于15%，连续5年净利润现金含量大于80%，连续5年毛利率大于30%，上市大于3年，连续5年资产负债率，派息比率'
    result = wc.search(s0)
    print(result)


cmd_list = [version, update]
for cmd in cmd_list:
    cli.add_command(cmd)


if __name__ == "__main__":
    cli()
