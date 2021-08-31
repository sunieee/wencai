# wencai

## 简单介绍

源Repository: [wencai](https://github.com/GraySilver/wencai)

其给出的wencai打包时遗漏了一个文件，需要复制过去：

```
pip install wencai
cd /anaconda3/lib/python3.7/site-packages/wencai/   # 对应wencai安装位置
mkdir js && cd js
wget 'http://sunie.top:9009/home/sunie/pythonFiles/utility/stock/wencai/wencai/js/hexin.js'
```

为了开发满足更多需求的wencai包，在原有的基础上fork了一份，添加命令行特性


## 安装方式

```
pip install http://sunie.tpddns.cn:9007/packages/wencai-0.0.2.sunie.2021_08_30t10_54-py3-none-any.whl
wc.util update
```

## 命令行组成模块

### wc.select


### wc.util