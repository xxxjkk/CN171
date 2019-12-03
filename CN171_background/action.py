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
                "_" + bg_action + "_" + datetime.now().strftime("%Y%m%d%H%M%S")
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


def checkResultAction():
    bg_opr_result = "执行中"
    bgTaskLogList = BgTaskLog.objects.filter(bg_opr_result=bg_opr_result)
    if bgTaskLogList:
        for i in bgTaskLogList:
            log_dir = i.bg_log_dir
            # downfilename = re.findall(r"/(.+?).log", log_dir)
            # log_dir_name = log_dir.split("/")
            # 适配Linux环境，截取日志文件名
            if '/' in log_dir:
                log_dir_name = log_dir.split('/')[-1]
            # 适配Windows环境，截取日志文件名
            elif '\\' in log_dir:
                log_dir_name = log_dir.split('\\')[-1]
            else:
                response = "Log file not exits!"
                return response
            # a = len(log_dir_name)
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
                    i.bg_operation_finish_time = datetime.now()
                elif i.bg_operation == "刷新":
                    i.bg_opr_result = "成功"
                    taskManagement.bg_status = "正常"
                    i.bg_operation_finish_time = datetime.now()
                else:
                    taskManagement.bg_status = "正常"
                    taskManagement.bg_lastopr_result = "成功"
                    i.bg_opr_result = "成功"
                    i.bg_operation_finish_time = datetime.now()
                remote_scp(log_dir, local_log_path)
            elif "中心总体状态：部分正常（满足最小集）" in log:
                if i.bg_operation == "刷新":
                    i.bg_opr_result = "成功"
                    i.bg_operation_finish_time = datetime.now()
                    taskManagement.bg_status = "部分正常"
                else:
                    taskManagement.bg_status = "部分正常"
                    taskManagement.bg_lastopr_result = "成功"
                    i.bg_opr_result = "失败"
                    i.bg_operation_finish_time = datetime.now()
                remote_scp(log_dir, local_log_path)
            elif "中心总体状态：异常" in log:
                if i.bg_operation == "刷新":
                    i.bg_opr_result = "成功"
                    taskManagement.bg_status = "异常"
                    i.bg_operation_finish_time = datetime.now()
                else:
                    taskManagement.bg_status = "异常"
                    taskManagement.bg_lastopr_result = "失败"
                    i.bg_operation_finish_time = datetime.now()
                    i.bg_opr_result = "失败"
                remote_scp(log_dir, local_log_path)
            elif "中心总体状态：停止" in log:
                if i.bg_operation == "停止":
                    taskManagement.bg_status = "停止"
                    taskManagement.bg_lastopr_result = "成功"
                    i.bg_operation_finish_time = datetime.now()
                    i.bg_opr_result = "成功"
                elif i.bg_operation == "刷新":
                    i.bg_opr_result = "成功"
                    i.bg_operation_finish_time = datetime.now()
                    taskManagement.bg_status = "停止"
                else:
                    taskManagement.bg_status = "停止"
                    taskManagement.bg_lastopr_result = "失败"
                    i.bg_opr_result = "失败"
                    i.bg_operation_finish_time = datetime.now()
                remote_scp(log_dir, local_log_path)
            elif "对不起，操作失败！" in log:
                if i.bg_operation == "刷新":
                    i.bg_opr_result = "失败"
                    taskManagement.bg_status = "异常"
                    i.bg_operation_finish_time = datetime.now()
                else:
                    print("因特殊原因，执行出错")
                    taskManagement.bg_status = "异常"
                    taskManagement.bg_lastopr_result = "失败"
                    i.bg_opr_result = "失败"
                    i.bg_operation_finish_time = datetime.now()
                remote_scp(log_dir, local_log_path)
            else:
                print("下个定时任务循环读取...")
            i.save()
            taskManagement.save()
    else:
        print("无可执行内容")


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