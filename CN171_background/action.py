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
config.read(os.path.join(BASE_DIR, 'config/cn171.conf'))
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
        cmd = taskManagement.bg_task_start + " >> " + file_name + "/" + file_name + ".log"
        taskManagement.bg_lastopr_type = "启动"
    elif bg_action == 'stop':
        cmd = taskManagement.bg_task_stop + " >> " + file_name + "/" + file_name + ".log"
        taskManagement.bg_lastopr_type = "停止"
    elif bg_action == 'restart':
        cmd = taskManagement.bg_task_restart + " >> " + file_name + "/" + file_name + ".log"
        taskManagement.bg_lastopr_type = "重启"
    elif bg_action == 'query':
        cmd = taskManagement.bg_task_query + " >> " + file_name + "/" + file_name + ".log"
        taskManagement.bg_lastopr_type = "刷新"
    else:
        return redirect("taskManagement")
    stdin, stdout, stderr = ssh_exec_cmd(sshd, cmd)
    err_list = stderr.readlines()
    if len(err_list) > 0:
        print('Start failed:' + err_list[0])
        returnmsg = "False"
        taskManagement.bg_lastopr_user = opr_user
        taskManagement.bg_lastopr_time = datetime.now()
        taskManagement.bg_lastopr_result = "失败"
        taskManagement.bg_status = bg_old_status
        taskManagement.save()
        bg_log = BgTaskLog.objects.get(bg_log_id=bg_log_id)
        bg_log.bg_operation = taskManagement.bg_lastopr_type
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
        taskManagement.bg_lastopr_user = opr_user
        taskManagement.bg_lastopr_result = "成功"
        taskManagement.bg_lastopr_time = datetime.now()
        taskManagement.save()
        bg_log = BgTaskLog.objects.get(bg_log_id=bg_log_id)
        bg_log.bg_opr_result = "执行中"
        bg_log.bg_operation = taskManagement.bg_lastopr_type
        bg_log_msg = str(bg_log.bg_operation_time) + ":" + \
                     bg_log.bg_operation_user + bg_log.bg_operation + '\n' + log_info
        # path = config.get('TaskManagement','log_path') + file_name + '.log'
        path = file_name + "/" + file_name + ".log"
        bg_log.bg_log_dir = path
        bg_log.save()
        returnmsg = "True"
    sshd.close()
    return returnmsg


# def checkResultAction():
#     bg_opr_result = "执行中"
#     bgTaskLogList = BgTaskLog.objects.filter(bg_opr_result=bg_opr_result)
#     if bgTaskLogList:
#         for i in bgTaskLogList:
#             log_dir = i.bg_log_dir
#             #downfilename = re.findall(r"/(.+?).log", log_dir)
#             #log_dir_name = log_dir.split("/")
#             # 适配Linux环境，截取日志文件名
#             if '/' in log_dir:
#                 log_dir_name = log_dir.split('/')[-1]
#             # 适配Windows环境，截取日志文件名
#             elif '\\' in log_dir:
#                 log_dir_name = log_dir.split('\\')[-1]
#             else:
#                 response = "Log file not exits!"
#                 return response
#             #a = len(log_dir_name)
#             downfilename = log_dir_name
#             filename = str(downfilename)
#             local_path = config.get('TaskManagement', 'log_path')
#             local_log_path = local_path + filename
#             i.bg_log_dir = local_log_path
#             i.save()
#             bg_id = i.bg_id
#             taskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
#             old_status = taskManagement.bg_status
#             log = readFile(log_dir)
#             if "中心总体状态：正常" in log:
#                 if i.bg_operation == "停止":
#                     taskManagement.bg_status = "正常"
#                     taskManagement.bg_lastopr_result = "失败"
#                     i.bg_opr_result = "失败"
#                 else:
#                     taskManagement.bg_status = "正常"
#                     taskManagement.bg_lastopr_result = "成功"
#                     i.bg_opr_result = "成功"
#             elif "中心总体状态：部分正常（满足最小集）" in log:
#                 taskManagement.bg_status = "部分正常"
#                 taskManagement.bg_lastopr_result = "成功"
#                 i.bg_opr_result = "失败"
#             elif "中心总体状态：异常" in log:
#                 taskManagement.bg_status = "异常"
#                 taskManagement.bg_lastopr_result = "失败"
#                 i.bg_opr_result = "失败"
#             elif "中心总体状态：停止" in log:
#                 if i.bg_operation == "停止":
#                     taskManagement.bg_status = "停止"
#                     taskManagement.bg_lastopr_result = "成功"
#                     i.bg_opr_result = "成功"
#                 else:
#                     taskManagement.bg_status = "停止"
#                     taskManagement.bg_lastopr_result = "失败"
#                     i.bg_opr_result = "失败"
#             elif "对不起，操作失败！" in log:
#                 print("因特殊原因，执行出错")
#                 taskManagement.bg_status = old_status
#                 taskManagement.bg_lastopr_result = "失败"
#                 i.bg_opr_result = "失败"
#             else:
#                 print("下个定时任务循环读取...")
#             remote_scp(log_dir, local_log_path)
#             i.save()
#             taskManagement.save()
#     else:
#         print("无可执行内容")