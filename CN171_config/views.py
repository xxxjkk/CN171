import os
from django.shortcuts import render
from django.http import JsonResponse
try:
    import ConfigParser as cp
except ImportError as e:
    import configparser as cp

#读取配置文件
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = cp.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config/cn171.conf'), encoding='utf-8')


#配置文件页面主函数
def configManagement(request):
    #获取配置文件中的sections，一维数组
    sectionlist = config.sections()

    #获取配置文件中的option和item，三维数组
    itemlist3 = []
    for section in sectionlist:
        items = config.items(section)
        itemlist3.append(items)

    return render(request,"config/config_management.html",locals())

#修改配置文件函数
def configSave(request):
    #获取界面传入的配置数据
    list_section = request.POST.getlist('list_section')
    list_value_str = request.POST.getlist('list_value')
    list_key_str = request.POST.getlist('list_key')
    list_value = []
    list_key = []
    for i in range(len(list_value_str)):
        list_value.append(list_value_str[i].split(','))
        list_key.append(list_key_str[i].split(','))

    #获取配置文件中的配置数据
    sectionlist = config.sections()
    keylist = []
    valuelist = []
    for section in sectionlist:
        options = config.options(section)
        keylist.append(options)

        templist = []
        for i in range(len(options)):
            templist.append(config.get(section,options[i]))
        valuelist.append(templist)

    #配置文件比对，存在差异的配置项，以前台传入的为主进行保存
    for i in range(len(sectionlist)):
        for j in range(len(keylist[i])):
            if valuelist[i][j] != list_value[i][j]:
                config.set(sectionlist[i], keylist[i][j], list_value[i][j])
    config.write(open(os.path.join(BASE_DIR, 'config/cn171.conf'), "w"))

    return JsonResponse({'executeflag': "成功"})


#修改配置文件函数
def reStartCN171(request):
    os.system(BASE_DIR + "/cn171.sh restart")

    return JsonResponse({'executeflag': "成功"})