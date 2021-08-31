import click
import os, sys
from wencai.util.utils import check_output, ech, now
import cProfile


filepath = os.path.dirname(os.path.abspath(__file__))  # 1. 源文件夹
src_path = os.path.dirname(filepath)   # 上一个文件夹

tmp_path = '/tmp/remote/profile/'
os.makedirs(tmp_path, exist_ok=True)

@click.group()
def cli():
    pass


@click.command()
@click.argument('args', nargs=-1)
def python(args):
    cmd = sys.argv
    cmd = cmd[cmd.index('python')+1:]
    out_prof = tmp_path + now() + '.prof'
    out_svg = tmp_path.replace('.prof', '.svg')
    launch_cmd = ['python', '-m', 'cProfile', '-o', out_prof] + cmd
    ech('launching %s' % click.style(' '.join(launch_cmd), 'blue'))
    os.system(' '.join(launch_cmd))
    ech(f'profile log is saved at {out_prof}', 'green')
    os.system(f'flameprof {out_prof} > {out_svg}')
    ech(f'{out_prof} -> {out_svg}', 'green')


cmd_list = [python]
for cmd in cmd_list:
    cli.add_command(cmd)

if __name__ == "__main__":
    cli()