#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2020/2/24 10:58
# @Author: zhaocy
# @File  : action.py
# @Software: CN171
from CN171_cmdb.models import CmdbApp, CmdbAppLog
from CN171_tools.connecttool import ssh_connect, ssh_exec_cmd, readFile, get_appmgnt_init_parameter, readAppLogFile


#app操控命令发送执行
def appTaskTest(ansible_host_appmgnt_return_filepath,ansible_host_appmgnt_applist_path,app_id, app_action, opr_user,applog_id):
    cmdbApp = CmdbApp.objects.get(app_id=app_id)
    applog = CmdbAppLog.objects.get(id=applog_id)
    #执行结果文件返回路径
    file_path_return = ansible_host_appmgnt_return_filepath
    #执行结果文件文件名
    file_name_return = opr_user + "_app_oneopr_return_" + app_action +applog.app_operation_time.strftime("%Y%m%d%H%M%S")
    conntarget = "Ansible"
    sshd = ssh_connect(conntarget)
    dir_cmd = "mkdir " + file_path_return
    ssh_exec_cmd(sshd, dir_cmd)
    cmd = "sh appopr.sh "+ " |tee -a " + file_path_return  + file_name_return + ".log"
    #cmd = "./clusterManagement.sh "+app_action+" "+file_name+" |tee -a " + file_path_return  + file_name_return + ".log"
    stdin, stdout, stderr = ssh_exec_cmd(sshd, cmd)
    err_list = stderr.readlines()
    if len(err_list) > 0:
        print('Start failed:' + err_list[0])
        returnmsg = "False"
        if app_action != 'status':
            cmdbApp.app_lastopr_result = "失败"
            applog.app_opr_result = "失败"
            cmdbApp.save()
    else:
        cmdbApp.app_lastopr_result = "执行中"
        applog.app_opr_result = "执行中"
        cmdbApp.app_status="4"
        print('Start success.')
        returnmsg = "True"
    cmdbApp.save()
    applog.save()
    sshd.close()
    return returnmsg

#app管理命令执行结果查询
def appOprResultCheck():
    applog = CmdbAppLog.objects.filter(app_opr_result="执行中")
    ansible_host_appmgnt_applist_path, ansible_host_appmgnt_return_filepath = get_appmgnt_init_parameter('Ansible')
    for i in applog:
        opr_user = i.app_operation_user
        app_id = i.app_id
        cmdbAppList = CmdbApp.objects.filter(app_id=app_id)
        cmdbApp=cmdbAppList[0]
        file_path_return = ansible_host_appmgnt_return_filepath
        resultfile = opr_user + "_app_oneopr_return_" + i.app_operation +i.app_operation_time.strftime("%Y%m%d%H%M%S")+".log"
        log = readAppLogFile(ansible_host_appmgnt_return_filepath+resultfile)
        if "应用的状态显示为：正常" in log:
            if i.app_operation=="stop" and i.app_lastopr_type=="restart":
                cmdbApp.app_status="1"
                cmdbApp.app_lastopr_result="成功"
                i.app_opr_result = "成功"
            elif i.app_operation=="stop":
                cmdbApp.app_status = "1"
                cmdbApp.app_lastopr_result = "失败"
                i.app_opr_result = "失败"
        elif  "应用的状态显示为：部分正常" in log:
            if i.app_operation=="status":
                cmdbApp.app_status="2"
                cmdbApp.app_lastopr_result = "成功"
                i.app_opr_result = "成功"
            else :
                cmdbApp.app_status = "2"
                cmdbApp.app_lastopr_result = "失败"
                i.app_opr_result = "失败"
        elif "应用的状态显示为：停止" in log:
            if i.app_operation == "stop" or i.app_operation == "status":
                cmdbApp.app_status = "3"
                cmdbApp.app_lastopr_result = "成功"
                i.app_opr_result = "成功"
            else:
                cmdbApp.app_status = "3"
                cmdbApp.app_lastopr_result = "失败"
                i.app_opr_result = "失败"
        else:
            print("下个定时任务循环读取...")
        i.save()
        cmdbApp.save()