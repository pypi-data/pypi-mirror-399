# ks_market_api
ks_market_api

conda install -c conda-forge ta-lib

pyinstaller  --hidden-import=Common_pb2  --hidden-import talib.stream  --paths=D:/ProgramData/Anaconda3/envs/vnpy/Lib/site-packages/futu/common/pb --add-data D:/ProgramData/Anaconda3/envs/vnpy/Lib/site-packages/futu/VERSION.txt;./futu  --add-data ./README.md;./ -i main.ico  -D   main.py --noconfirm

# todo 运行满一个整点之后可能会出现关不掉进程的问题