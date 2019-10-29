#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/10/28 9:27
# @Author: zhaocy
# @File  : task.py
# @Software: CN171

#调用celery中的task模块
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.shortcuts import redirect

import os
from datetime import datetime
from CN171_background.models import BgTaskManagement, BgTaskLog
from CN171_tools.connecttool import ssh_connect, ssh_exec_cmd

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

@shared_task
def taskOne(bg_id,bg_action,opr_user):
    log_info = "执行情况\n"
    taskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
    old_status = taskManagement.bg_status
    conntarget = "Ansible"
    sshd = ssh_connect(conntarget)

    if bg_action == 'start':
        cmd = taskManagement.bg_task_start
        taskManagement.bg_lastopr_type = "启动"
    elif bg_action == 'stop':
        cmd = taskManagement.bg_task_stop
        taskManagement.bg_lastopr_type = "停止"
    elif bg_action == 'restart':
        cmd = taskManagement.bg_task_restart
        taskManagement.bg_lastopr_type = "重启"
    elif bg_action == 'query':
        cmd = taskManagement.bg_task_query
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
        taskManagement.bg_status = old_status
        taskManagement.save()
        bg_log = BgTaskLog()
        bg_log.bg_id = bg_id
        bg_log.bg_operation = taskManagement.bg_lastopr_type + taskManagement.bg_module + taskManagement.bg_domain
        bg_log.bg_operation_time = datetime.now()
        bg_log.bg_operation_user = opr_user
        bg_log.bg_opr_result = "失败"
        # 写入日志文件
        file_name = taskManagement.bg_module + "_" + taskManagement.bg_domain + \
                    "_" + "start" + "_" + datetime.now().strftime("%Y%m%d%H%I%S")
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
        for item in stdout.readlines():
            log_info = log_info + item
            print(item)
            if "中心总体状态：正常" in item:
                taskManagement.bg_status = "正常"
            elif "中心总体状态：部分正常（满足最小集）" in item:
                taskManagement.bg_status = "部分正常"
            elif "中心总体状态：异常" in item:
                taskManagement.bg_status = "异常"
            elif "中心总体状态：停止" in item:
                taskManagement.bg_status = "停止"
            elif "对不起，操作失败！" in item:
                print("因特殊原因，执行出错")
                taskManagement.bg_status = "停止"
            else:
                print("循环读取...")
        taskManagement.bg_lastopr_user = opr_user
        taskManagement.bg_lastopr_result = "成功"
        taskManagement.bg_lastopr_time = datetime.now()
        taskManagement.save()
        bg_log = BgTaskLog()
        bg_log.bg_id = bg_id
        bg_log.bg_operation = taskManagement.bg_lastopr_type + taskManagement.bg_module + taskManagement.bg_domain
        bg_log.bg_operation_time = datetime.now()
        bg_log.bg_operation_user = opr_user
        bg_log.bg_opr_result = "成功"
        # 写入日志文件
        file_name = taskManagement.bg_module + "_" + taskManagement.bg_domain + \
                    "_" + "start" + "_" + datetime.now().strftime("%Y%m%d%H%I%S")
        # str不支持时间格式直接相加
        bg_log_msg = str(bg_log.bg_operation_time) + ":" + \
                     bg_log.bg_operation_user + bg_log.bg_operation + '\n' + log_info
        path = config.get(
            'TaskManagement',
            'log_path') + file_name + '.log'
        bg_log.bg_log_dir = path
        file = open(path, 'a+')
        file.write(bg_log_msg)  # msg也就是下面的Hello world!
        file.close()
        bg_log.save()
        returnmsg = "True"
    sshd.close()
    return returnmsg



