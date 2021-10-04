from PIL import Image
import torch
from torchvision.transforms.functional import to_tensor, to_pil_image

from captcha_break.code.utils import Char, CaptchaDataset
import os
import sys

lowercase = True

img = Image.open('/tmp/wencai/tmp.png')
print(img.size)

pil_to_tensor()
char = Char(lowercase)
width, height, n_len, n_classes = 192, 64, 4, char.length  # 192 64
n_input_length = 12
print(char.characters, width, height, n_len, n_classes)


dataset = CaptchaDataset(char, 1, width, height, n_input_length, n_len)
image, target, input_length, label_length = dataset[0]
print(''.join([char.characters[x]
               for x in target]), input_length, label_length)
to_pil_image(image)

filepath = os.path.dirname(os.path.abspath(__file__))  # 1. 源文件夹
sys.path.append(f'{filepath}/captcha_break/code/')
model = torch.load(f'{filepath}/captcha_break/model/ctc_lower_2021.pth')

model.eval()
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
