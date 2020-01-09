#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/12/11 10:41
# @Author: zhaocy
# @File  : action.py
# @Software: CN171
# 容量预测生成指令异步发送
import os

from CN171_aiops import models
from CN171_aiops.excelutil import resultExcelRead
from CN171_tools.connecttool import ssh_connect, ssh_exec_cmd, remote_scp

try:
    import ConfigParser as cp
except ImportError as e:
    import configparser as cp

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = cp.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config/cn171.conf'),encoding='utf-8')

def taskAction(id,DB_Name,tablespace_name,start_time,end_time,alarm_threshold):
    conntarget = "Ansible_bg"
    sshd = ssh_connect(conntarget)
    # 待补充脚本参数
    cmd = "python /home/zhaocy/tasktest/timeprint.py "
    stdin, stdout, stderr = ssh_exec_cmd(sshd, cmd)
    err_list = stderr.readlines()
    aiopsDetectLog = models.AiopsDetectLog.objects.get(id=id)
    if len(err_list) > 0:
        print('Start failed:' + err_list[0])
        returnmsg = "False"
        aiopsDetectLog.status = "失败"
    else:
        aiopsDetectLog.status = "生成中"
        print('Start success.')
        aiopsDetectLog.save()
        returnmsg = "True"
    sshd.close()
    return returnmsg

# 检查生成情况
def checkGenerate():
    aiopsDetectLog = models.AiopsDetectLog.objects.filter(status="生成中")
    for i in aiopsDetectLog:
        filepath = "tasktest/"
        tablespacedict = i.ai_tablespacedict
        create_time = i.create_time.strftime("%Y%m%d%H%M%S")
        filename = i.ai_tablespacedict.DB_Name+"_"+tablespacedict.tablespace_name+"_"+create_time+".xls"
        resultFilePath = filepath+filename
        local_path = config.get('AIopsCapacity', 'AIopsCapacity_result_path')
        local_path_name = local_path+filename
        remote_scp(resultFilePath, local_path_name)
        resultExcelRead(local_path_name,filename)
        i.status = "完成"
        i.save()
    return None

