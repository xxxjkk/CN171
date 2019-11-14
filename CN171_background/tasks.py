#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/10/28 9:27
# @Author: zhaocy
# @File  : task.py
# @Software: CN171

#调用celery中的task模块
from __future__ import absolute_import, unicode_literals

import re

from celery import shared_task
from django.shortcuts import redirect

import os
from datetime import datetime

from CN171_background.action import taskOneAction, reLoadAction
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

@shared_task
def taskOne(bg_id,bg_action,opr_user,bg_log_id,bg_old_status):
    taskOneAction(bg_id,bg_action,opr_user,bg_log_id,bg_old_status)

@shared_task
def checkResult():
    bg_opr_result = "执行中"
    bgTaskLogList = BgTaskLog.objects.filter(bg_opr_result=bg_opr_result)
    if bgTaskLogList:
        for i in bgTaskLogList:
            log_dir = i.bg_log_dir
            #downfilename = re.findall(r"/(.+?).log", log_dir)
            #log_dir_name = log_dir.split("/")
            # 适配Linux环境，截取日志文件名
            if '/' in log_dir:
                log_dir_name = log_dir.split('/')[-1]
            # 适配Windows环境，截取日志文件名
            elif '\\' in log_dir:
                log_dir_name = log_dir.split('\\')[-1]
            else:
                response = "Log file not exits!"
                return response
            #a = len(log_dir_name)
            downfilename = log_dir_name
            filename = str(downfilename)
            local_path = config.get('TaskManagement', 'log_path')
            local_log_path = local_path + filename
            i.bg_log_dir = local_log_path
            i.save()
            bg_id = i.bg_id
            taskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
            old_status = taskManagement.bg_status
            log = readFile(log_dir)
            if "中心总体状态：正常" in log:
                if i.bg_operation == "停止":
                    taskManagement.bg_status = "正常"
                    taskManagement.bg_lastopr_result = "失败"
                    i.bg_opr_result = "失败"
                else:
                    taskManagement.bg_status = "正常"
                    taskManagement.bg_lastopr_result = "成功"
                    i.bg_opr_result = "成功"
                remote_scp(log_dir, local_log_path)
            elif "中心总体状态：部分正常（满足最小集）" in log:
                if i.bg_operation == "刷新":
                    taskManagement.bg_status = "部分正常"
                    taskManagement.bg_lastopr_result = "成功"
                    i.bg_opr_result = "成功"
                else:
                    taskManagement.bg_status = "部分正常"
                    taskManagement.bg_lastopr_result = "成功"
                    i.bg_opr_result = "失败"
                remote_scp(log_dir, local_log_path)
            elif "中心总体状态：异常" in log:
                if i.bg_operation == "刷新":
                    taskManagement.bg_status = "异常"
                    taskManagement.bg_lastopr_result = "成功"
                    i.bg_opr_result = "成功"
                else:
                    taskManagement.bg_status = "异常"
                    taskManagement.bg_lastopr_result = "失败"
                    i.bg_opr_result = "失败"
                remote_scp(log_dir, local_log_path)
            elif "中心总体状态：停止" in log:
                if i.bg_operation == "停止":
                    taskManagement.bg_status = "停止"
                    taskManagement.bg_lastopr_result = "成功"
                    i.bg_opr_result = "成功"
                elif i.bg_operation == "刷新":
                    taskManagement.bg_status = "停止"
                    taskManagement.bg_lastopr_result = "成功"
                    i.bg_opr_result = "成功"
                else:
                    taskManagement.bg_status = "停止"
                    taskManagement.bg_lastopr_result = "失败"
                    i.bg_opr_result = "失败"
                remote_scp(log_dir, local_log_path)
            elif "对不起，操作失败！" in log:
                print("因特殊原因，执行出错")
                taskManagement.bg_status = old_status
                taskManagement.bg_lastopr_result = "失败"
                i.bg_opr_result = "失败"
                remote_scp(log_dir, local_log_path)
            else:
                print("下个定时任务循环读取...")
            i.save()
            taskManagement.save()
    else:
        print("无可执行内容")


@shared_task
def taskReload():
    reLoadAction()
