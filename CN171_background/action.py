#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/10/30 11:36
# @Author: zhaocy
# @File  : action.py
# @Software: CN171
from __future__ import absolute_import, unicode_literals

import re
import sys

from celery import shared_task
from django.shortcuts import redirect

import os
from datetime import datetime
from CN171_background.models import BgTaskManagement, BgTaskLog
from CN171_tools.connecttool import ssh_connect, ssh_exec_cmd, readFile, get_init_parameter, remote_scp

try:
    import ConfigParser as cp
except ImportError as e:
    import configparser as cp
# 后台管理函数
from CN171_tools.connecttool import ssh_close, ssh_connect, ssh_exec_cmd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = cp.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config/cn171.conf'),encoding='utf-8')
conntarget = "Ansible"

def taskOneAction(bg_id,bg_action,opr_user,bg_log_id,bg_old_status):
    log_info = "执行情况\n"
    taskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
    file_name = taskManagement.bg_module + "_" + taskManagement.bg_domain + \
                "_" + bg_action + "_" + datetime.now().strftime("%Y%m%d%H%I%S")
    conntarget = "Ansible"
    sshd = ssh_connect(conntarget)
    dir_cmd = "mkdir "+ file_name
    ssh_exec_cmd(sshd, dir_cmd)
    if bg_action == 'start':
        cmd = taskManagement.bg_task_start + "  |tee -a " + file_name + "/" + file_name + ".log"
    elif bg_action == 'stop':
        cmd = taskManagement.bg_task_stop + "  |tee -a " + file_name + "/" + file_name + ".log"
    elif bg_action == 'restart':
        cmd = taskManagement.bg_task_restart + "  |tee -a " + file_name + "/" + file_name + ".log"
    elif bg_action == 'query':
        cmd = taskManagement.bg_task_query + "  |tee -a " + file_name + "/" + file_name + ".log"
    else:
        return redirect("taskManagement")
    stdin, stdout, stderr = ssh_exec_cmd(sshd, cmd)
    err_list = stderr.readlines()
    if len(err_list) > 0:
        print('Start failed:' + err_list[0])
        returnmsg = "False"
        if bg_action != 'query':
            taskManagement.bg_lastopr_result = "失败"
            taskManagement.bg_status = bg_old_status
            taskManagement.save()
        bg_log = BgTaskLog.objects.get(bg_log_id=bg_log_id)

        bg_log.bg_opr_result = "失败"
        # 写入日志文件
        bg_log_msg = str(bg_log.bg_operation_time) + ":" + \
                     bg_log.bg_operation_user + bg_log.bg_operation + bg_log.bg_opr_result + "\n执行情况：\n" + err_list[0]
        path = config.get('TaskManagement', 'log_path') + file_name + '.log'
        bg_log.bg_log_dir = path
        file = open(path, 'a+')
        file.write(bg_log_msg)
        file.close()
        bg_log.save()
    else:
        print('Start success.')
        bg_log = BgTaskLog.objects.get(bg_log_id=bg_log_id)
        bg_log.bg_opr_result = "执行中"
        bg_log_msg = str(bg_log.bg_operation_time) + ":" + \
                     bg_log.bg_operation_user + bg_log.bg_operation + '\n' + log_info
        # path = config.get('TaskManagement','log_path') + file_name + '.log'
        path = file_name + "/" + file_name + ".log"
        bg_log.bg_log_dir = path
        bg_log.save()
        returnmsg = "True"
    sshd.close()
    return returnmsg


#def checkResultAction():


#刷新状态定时任务
def reLoadAction():
    idlist = BgTaskManagement.objects.values_list('bg_id', flat=True)
    bg_action = 'query'
    opr_user = "后台定时刷新"
    for bg_id in idlist:
        bgTaskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
        bg_old_status = bgTaskManagement.bg_status
        if bgTaskManagement.bg_status != "进行中":
            bgTaskManagement.bg_status = "进行中"
            bgTaskManagement.save()
            bg_log = BgTaskLog()
            bg_log.bg_id = bg_id
            bg_log.bg_operation_time = datetime.now()
            bg_log.bg_operation_user = opr_user
            bg_log.bg_opr_result = "待执行"
            # 写入日志文件
            bg_log.save()
            bg_log_id = bg_log.bg_log_id
            taskOneAction(bg_id, bg_action, opr_user, bg_log_id, bg_old_status)
            returnmsg = "True"
        else:
            returnmsg = "False"