from PIL import Image
import torch
from torchvision.transforms.functional import to_pil_image, pil_to_tensor

import os
import sys
import numpy as np
import click

from wencai.util.utils import ech

filepath = os.path.dirname(os.path.abspath(__file__))  # 1. 源文件夹


@click.group()
def cli():
    pass


def load_model(path, codepath=None):    # 在torch文件夹下对应模型位置，代码默认放在 model同目录的code文件夹下
    absolutepath = f'{filepath}/{path}'
    dirpath = os.path.dirname(absolutepath)
    os.makedirs(dirpath, exist_ok=True)
    if not codepath:
        codepath = f'{os.path.dirname(dirpath)}/code'
    sys.path.append(codepath)

    if not os.path.exists(absolutepath):
        ech(f'Model {path} does not exist. Downloding...', 'yellow')
        import requests
        import time
        # http://d.sunie.top:9009/home/sunie/Desktop/pythonFiles/wencai/wencai/torch/captcha_break/model/ctc_lower_2021.pth
        url = 'http://d.sunie.top:9009/home/sunie/Desktop/pythonFiles/wencai/wencai/torch/'
        r = requests.get(url + path, stream=True)
        with open(absolutepath, 'wb') as f:
            for chunck in r.iter_content(chunk_size=512):
                if chunck:
                    f.write(chunck)
        time.sleep(1)
        ech(f'Model {path} download successfully!', 'green')
    else:
        ech(f'Model {path} already exists!', 'green')
    # print(dirpath)

    model = torch.load(absolutepath)
    model.eval()
    return model


@click.command()
@click.argument("path")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-l", "--lowercase", is_flag=True)
def OCR(path, verbose, lowercase):
    __OCR(path, verbose, lowercase)


def __OCR(path='/tmp/wencai/tmp.png', verbose=False, lowercase=True):
    # 改变图像的位深度： https://blog.csdn.net/weixin_39190382/article/details/105917690
    from captcha_break.code.utils import Char
    char = Char(lowercase)
    model = load_model('captcha_break/model/ctc_lower_2021.pth')

    img = Image.open(path)
    img = img.resize((192, 64))
    img = img.convert("RGB")
    # print(img.getbands())

    if verbose:
        print(np.array(img).shape)
        img.save('/tmp/wencai/1.png')

    image = pil_to_tensor(img)

    if verbose:
        to_pil_image(image).save('/tmp/wencai/2.png')
        print(image.numpy())

    # image = torch.cat((image, image, image), 0)
    # print(image.shape)
    image = image.float() / 256

    if verbose:
        print(image.numpy())
        to_pil_image(image).save('/tmp/wencai/3.png')

    output = model(image.unsqueeze(0).cuda())
    output_argmax = output.detach().permute(1, 0, 2).argmax(dim=-1)
    pred = char.decode(output_argmax[0])
    print(f'prediction: {pred}')
    return pred


def OCRtest(lowercase=True):
    from captcha_break.code.utils import Char, CaptchaDataset
    char = Char(lowercase)
    model = load_model('captcha_break/model/ctc_lower_2021.pth')

    width, height, n_len, n_classes = 192, 64, 4, char.length  # 192 64
    n_input_length = 12

    dataset = CaptchaDataset(char, 1, width, height, n_input_length, n_len)
    image, target, input_length, label_length = dataset[0]
    print(image.shape)
    print(image.numpy())
    print(''.join([char.characters[x]
                   for x in target]), input_length, label_length)
    to_pil_image(image).save('/tmp/wencai/output.png')

    output = model(image.unsqueeze(0).cuda())
    output_argmax = output.detach().permute(1, 0, 2).argmax(dim=-1)
    do = True
    while do or char.decode_target(target) == char.decode(output_argmax[0]):
        do = False
        image, target, input_length, label_length = dataset[0]
        print('true:', char.decode_target(target))

        output = model(image.unsqueeze(0).cuda())
        output_argmax = output.detach().permute(1, 0, 2).argmax(dim=-1)
        print('pred:', char.decode(output_argmax[0]))
    to_pil_image(image)


cmd_list = [OCR]
for cmd in cmd_list:
    cli.add_command(cmd)


if __name__ == "__main__":
    # cli()
    __OCR()
