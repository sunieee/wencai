import click
from wencai import __version__
from wencai.util.utils import ech
from wencai.core.crawler import Wencai

wc = Wencai(cn_col=True)


@click.group()
def cli():
    pass


def __search(conditions):
    s0 = '，'.join(conditions)
    ech("正在查询: %s" % click.style(s0, 'blue'))
    result = wc.search(s0)
    return result


@click.command()
@click.argument('conditions', nargs=-1)
def search(conditions):
    """search target string in iwencai.com"""
    if len(conditions) == 0:
        conditions = ['连续5年ROE大于15%', '连续5年净利润现金含量大于80%', '连续5年毛利率大于30%', '上市大于3年', '连续5年资产负债率', '派息比率']
    result = __search(conditions)
    print(result)


cmd_list = [search]
for cmd in cmd_list:
    cli.add_command(cmd)


if __name__ == "__main__":
    cli()
