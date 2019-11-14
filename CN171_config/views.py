import os
from django.shortcuts import render
try:
    import ConfigParser as cp
except ImportError as e:
    import configparser as cp

#读取配置文件
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = cp.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config/cn171.conf'),encoding='utf-8')


def configManagement(request):
    #获取配置文件中的sections
    print(config.sections())
    sectionlist = config.sections()
    print(config.items(sectionlist[0]))
    items = config.items(sectionlist[0])

    return render(request,"config/config_management.html",locals())