import click
import pandas as pd
import os
from wencai.remote.wechat import send_text
from wencai import __version__


filepath = os.path.dirname(os.path.abspath(__file__))  # 1. 源文件夹
src_path = os.path.dirname(filepath)   # 上一个文件夹

@click.group()
def cli():
    pass


@click.command()
def rsync():
    pass


@click.command()
@click.argument('content', nargs=-1)
def send(content):
    send_text('\n'.join(content))


cmd_list = [rsync, send]
for cmd in cmd_list:
    cli.add_command(cmd)

if __name__ == "__main__":
    cli()