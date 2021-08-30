import click
import pandas as pd
import os
from wencai.util.utils import des_decrypt, des_encrypt, ech, get_newest_version
from wencai import __version__


filepath = os.path.dirname(os.path.abspath(__file__))  # 1. 源文件夹
src_path = os.path.dirname(filepath)   # 上一个文件夹


@click.group()
def cli():
    pass

@click.command()
@click.argument('password')
@click.option('-k', '--key', default=None, help="using target secret key to encrypt, mac address on default")
def encrypt(password, key):
    ech(des_encrypt(password, key), 'blue')


@click.command()
@click.argument('password')
@click.option('-k', '--key', default=None, help="using target secret key to encrypt, mac address on default")
def decrypt(password, key):
    ech(des_decrypt(password, key), 'blue')


@click.command()
def upload():
    os.system(f'sh {src_path}/sh/upload.sh')


@click.command()
@click.option('-b', '--branch', default='sunie', help="spring branch to update")
def update(branch):
    """update wencai to the newest version"""
    ech('on branch: %s' % click.style(branch, 'blue'))
    version = get_newest_version(branch)
    ech('the newest version is: %s' % click.style(version, 'blue'))
    os.system("pip install http://sunie.tpddns.cn:9007/packages/" + f"wencai-{version}-py3-none-any.whl  --user --upgrade")
    ech(f'successfully update wencai({version})', 'green')


@click.command()
def version():
    print(__version__)


@click.command()
@click.argument('filepath')
def pdf2txt(filepath):
    from wencai.util.utils import Pdf2Txt, pre_process
    # src = 'core_qmof_pdf/'
    if filepath[0] != '/':
        filepath = os.path.join(os.getcwd(), filepath)

    s = Pdf2Txt(filepath)
    s = pre_process(s)
    ech('The result txt is:', 'yellow')
    ech(s)


@click.command()
@click.argument('folder')
@click.option('-f', '--fps', default=1)
def pic2gif(folder, fps):
    from moviepy.editor import ImageSequenceClip
    from wencai.util.utils import sort_filename
    import os
    
    if folder[0] != '/':
        folder = os.path.join(os.getcwd(), folder)
    dst = os.path.join(folder, 'demo.gif')

    img_names = [t for t in os.listdir(folder) if t[-4:] in ['.png', '.jpg']]
    img_names = sort_filename(img_names)

    ech("converting files at: %s" % click.style(folder, 'blue'))
    ech(','.join(img_names), 'blue')
    clip = ImageSequenceClip([os.join(folder, t) for t in img_names], fps=fps)
    clip.write_gif(dst)


@click.command()
@click.argument('file', help='bib file you want to convert')
def bib2buaa(file):
    from wencai.util.inproceedings import Bib, Name
    df = pd.DataFrame(columns=['name', 'count', 'papers'])

    ech('buaa format txt:', 'yellow')
    with open(file, "r", encoding='utf-8') as f:
        lines = f.readlines()
        lines.append("\n")
        string = ""
        for line in lines:
            if len(line.strip()) == 0:
                if len(string)>0:
                    print(Bib(string).to_buaa())
                    string = ""
            else:
                string += line

    name_map = Name.name2paper
    ech('name_map:', 'yellow')
    print(name_map)

    i = 0
    for name, papers in name_map.items():
        df.loc[i] = {'name': name, 'count': len(papers), 'papers': str(papers)}
        i += 1
    ech('dataframe', 'yellow')
    print(df)


@click.command()
def init():
    """安装其他依赖"""
    os.system('pip install pyDes')
    os.system('pip install comtypes')
    os.system('pip install moviepy --ignore-installed imageio')


cmd_list = [encrypt, decrypt, upload, update, version, pdf2txt, pic2gif, init, bib2buaa]
for cmd in cmd_list:
    cli.add_command(cmd)

if __name__ == "__main__":
    cli()
