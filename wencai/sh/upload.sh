# pip install wheel twine

cd /home/sunie/Desktop/pythonFiles/wencai
rm -rf build
rm -rf dist
rm -rf wencai.egg-info
python setup.py bdist_wheel
twine upload dist/* -r private --verbose

# pip install http://sunie.tpddns.cn:9007/packages/wencai-0.0.1.sunie.2021_08_25t10_26-py3-none-any.whl
conda activate
wc.util update
