import click
import os
from wencai.util.utils import des_decrypt, des_encrypt, ech
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
@click.argument('filepath')
@click.option('-o', '--output', default=None)
@click.option('-p', '--preprocess', is_flag=True)
def totxt(filepath, output, preprocess):
    """将pdf, word, html转txt"""
    from wencai.util.utils import pre_process
    from wencai.util.convert import word2txt, html2txt, pdf2txt
    if filepath.endswith('.pdf'):
        s = pdf2txt(filepath)
    elif filepath.endswith('.docx') or filepath.endswith('.doc'):
        s = word2txt(filepath)
    elif filepath.endswith('.html'):
        s = html2txt(filepath)
    else:
        with open(filepath, 'r') as f:
            s = f.read()

    if preprocess:
        s = pre_process(s)
    if output:
        ech(f'totxt: {filepath} -> {output}')
        with open(output, 'w') as f:
            f.write(s)
    ech('The result txt is:', 'yellow')
    ech(s)


@click.command()
@click.argument('folder')
@click.option('-f', '--fps', default=1)
def pic2gif(folder, fps):
    """将一系列图片转化为gif动图"""
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
@click.argument('file')
def bib2buaa(file):
    """将bib转为buaa格式的文献引用"""
    from wencai.util.inproceedings import Bib, Name
    import pandas as pd
    df = pd.DataFrame(columns=['name', 'count', 'papers'])

    ech('buaa format txt:', 'yellow')
    with open(file, "r", encoding='utf-8') as f:
        lines = f.readlines()
        lines.append("\n")
        string = ""
        for line in lines:
            if len(line.strip()) == 0:
                if len(string) > 0:
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
@click.option('-u', '--user', is_flag=True)
def init(user):
    """安装其他较大依赖"""
    with open(os.path.join(filepath, 'requirements.txt'), 'r') as f:
        s = f.readlines()
    for line in s:
        cmd = f'pip install {line}'
        if user:
            cmd += ' --user'
        os.system(cmd)


@click.command()
def clean():
    with open(os.path.join(filepath, 'requirements.txt'), 'r') as f:
        s = f.readlines()
    for line in s:
        os.system(f'pip uninstall -y {line.split()[0]}')
    os.system('pip uninstall -y docx')


@click.command()
@click.argument('src')
@click.option('-o', '--output', default=None)
@click.option('-l', '--line-max', default=2, type=int, help="每行最多个数")
@click.option('-v', '--vertical', is_flag=True)
@click.option('-z', '--zoom', default=1, type=float)
@click.option('-r', '--row-max', default=None, type=int, help="每个pdf最多行数")
def pdfview(src, output, line_max, vertical, zoom, row_max):
    """将pdf每n页合成一页"""
    from wencai.util.convert import pdf2jpg, concat_pic_pdf
    from wencai.util.utils import get_tmp_path
    tmp_path = os.path.join(get_tmp_path(), 'tmp')
    import shutil
    shutil.rmtree(tmp_path, ignore_errors=True)
    pdf2jpg(src, tmp_path, zoom)
    concat_pic_pdf(tmp_path, output, vertical=vertical,
                   line_max=line_max, row_max=row_max)


cmd_list = [encrypt, decrypt, totxt, pic2gif, init, bib2buaa, pdfview, clean]
for cmd in cmd_list:
    cli.add_command(cmd)


if __name__ == "__main__":
    cli()
