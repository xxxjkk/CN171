#!/usr/bin/env python

import os,shutil
import time

from CN171_aiops.models import PbossWarningKPI

try:
    import ConfigParser as cp
except ImportError as e:
    import configparser as cp

#采集间隔（以分钟为单位）
INTERVAL = 30

#读取配置文件
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = cp.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config/cn171.conf'), encoding='utf-8')

#文件路径和备份路径
local_filedir = config.get('WARNING', 'pboss_warning_local_filedir')
local_filebakdir = config.get('WARNING', 'pboss_warning_local_filedirbak')

#text文件读取主函数
def textRead():
    #获取文件夹下的所有文件
    files = os.listdir(local_filedir)

    for file in files:
        #判断是否为以PBOSS开头、.txt结尾的text文件
        file_name = file.split('.')[0]
        file_ext = file.split('.')[1]
        if ('txt' == file_ext) and (file.startswith('PBOSS')):
            file_type = file_name.split('_')[1]
            file_time = str(file_name.split('_')[2])
            if file_type == 'WARNING' and isVaildTime(file_time):
                warningTextAnalysis(file)
            else:
                print("未知类型文件《" + file + "》，不进行处理")
        time.sleep(1)

#判断是否是有效的时间
def isVaildTime(file_time):
    try:
        starttime = time.strptime(file_time, "%Y%m%d%H%M")
        if starttime.tm_min % INTERVAL == 0:
            return True
        else:
            return False
    except:
        return False

def warningTextAnalysis(file):
    srcfile = local_filedir + file
    dstfile = local_filebakdir + file

    runtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    f = open(srcfile)
    lines = f.readline()
    kpi = lines.split('#')

    pbswarning_kpi = PbossWarningKPI()
    pbswarning_kpi.warning_runtime = runtime
    pbswarning_kpi.warning_interface_success1 = kpi[0]
    pbswarning_kpi.warning_interface_success2 = kpi[1]
    pbswarning_kpi.warning_service_success = kpi[2]
    pbswarning_kpi.warning_query_success = kpi[3]
    pbswarning_kpi.save()

    f.close();

    # 文件迁移
    shutil.move(srcfile, dstfile)

    return None