#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/10/28 9:27
# @Author: zhaocy
# @File  : task.py
# @Software: CN171

#调用celery中的task模块
from __future__ import absolute_import, unicode_literals

import re
from datetime import datetime

from celery import shared_task
from django.http import request
from django.shortcuts import redirect

import os

from CN171_background.models import BgTaskManagement
from CN171_cmdb.action import appTaskTest, appOprResultCheck
from CN171_cmdb.models import CmdbHost, CmdbApp, CmdbAppCluster, CLUSTER_STATUS, APP_STATUS, CmdbAppLog
from CN171_tools.common_api import get_tuple_key
from CN171_tools.connecttool import remote_scp, readFile, ssh_connect, ssh_exec_cmd, get_hostmgnt_init_parameter, \
    get_appmgnt_cluster_init_parameter, get_appmgnt_init_parameter, readAppLogFile
from CN171_tools.sftputils import remote_scp1

#批量刷新主机状态任务
@shared_task
def batchRefreshHostStatusTask(ansible_host_hostmgnt_return_filepath,user_name,ansible_host_hostmgnt_scrideploy_path):
    returnmsg = "False"

    file_path_return = ansible_host_hostmgnt_return_filepath
    file_name_return = user_name+"_refresh_host_status_return"
    conntarget = "Ansible"
    sshd = ssh_connect(conntarget)
    dir_cmd = "mkdir "+ file_path_return
    ssh_exec_cmd(sshd, dir_cmd)

    #cmd = "python3 osproject/bin/mach_get.py " + " >> " + file_path_return + "/" + file_name_return + ".log"
    cmd = "python "+ansible_host_hostmgnt_scrideploy_path+"mach_get.py " + " >> " + file_path_return + "/" + file_name_return + ".log"
    stdin, stdout, stderr = ssh_exec_cmd(sshd, cmd)
    err_list = stderr.readlines()
    if len(err_list) > 0:
        print('Refresh failed:' + err_list[0])
    else:
        print('Start success.')
        returnmsg = "True"
    sshd.close()
    return returnmsg

#批量刷新集群状态任务
@shared_task
def batchRefreshClusterStatusTask(ansible_cmdb_appmgnt_clusterReturn_filepath,user_name,logId):
    print("开始执行---------------------")
    cmdbAppLog = CmdbAppLog.objects.get(id = logId)
    returnmsg = "False"
    file_path_return = ansible_cmdb_appmgnt_clusterReturn_filepath
    nowTime = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name_return = "refresh_cluster_status_return_"+str(logId)
    conntarget = "Ansible"
    sshd = ssh_connect(conntarget)
    cmd = "sh appbatchopr.sh " + " >> " + file_path_return + "/" + file_name_return + ".log"
    #cmd = "./clusterManagement.sh status" + " >> " + file_path_return + "/" + file_name_return + ".log"
    stdin, stdout, stderr = ssh_exec_cmd(sshd, cmd)
    err_list = stderr.readlines()
    if len(err_list) > 0:
        print('Refresh failed:' + err_list[0])
    else:
        cmdbAppLog.app_opr_result = "集群刷新执行中"
        cmdbAppLog.save()
        print('Start success.')
        returnmsg = "True"
    sshd.close()
    return returnmsg


def local_log_path(args):
    pass

#异步查询主机状态结果
@shared_task
def checkHostStatusResult():
    #返回的日志文件名
    return_log_file=request.session.get('user_name')+"_refresh_host_status_return.log"
    #获取返回的文件路径
    ansible_host_hostmgnt_busiip_path, ansible_host_hostmgnt_return_filepath, ansible_host_hostmgnt_scrideploy_path \
        = get_hostmgnt_init_parameter('Ansible')
    #返回文件的带绝对路径的文件
    return_log_file_name = ansible_host_hostmgnt_return_filepath+return_log_file
    #返回文件写入本地的目录
    local_log_path="D:/temp/cmdb/hostmgnt/status/retlog/"
    log = readFile(return_log_file_name)
    if log:
        if "End" in log:
            remote_scp1(return_log_file_name, local_log_path)
            #读取.txt文件
            with open(local_log_path+return_log_file , 'r') as pfp:
                #循环读取每一行的数据
                for line in pfp.readlines():
                    if "start to collect" in line:
                        continue
                    elif "End" in line:
                        break
                    else:
                        refreshHostStatus(line)
        else:
            print("下个定时任务循环读取...")
    else:
        print("无可执行内容")

#异步查询集群状态结果
@shared_task
def checkClusterStatusResult():
    #返回的日志文件名
    applogList = CmdbAppLog.objects.filter(app_opr_result="集群刷新执行中")
    for i in applogList:
        return_log_file = "refresh_cluster_status_return_"+str(i.id)+".log"
        # 获取返回的文件路径
        ansible_cmdb_appmgnt_appClusterlist_path, ansible_cmdb_appmgnt_clusterReturn_filepath = get_appmgnt_cluster_init_parameter(
            'Ansible')

        # 返回文件的带绝对路径的文件
        return_log_file_name = ansible_cmdb_appmgnt_clusterReturn_filepath + return_log_file
        # 返回文件写入本地的目录
        local_log_path = "D:/temp/cmdb/appmgnt/cluster/status/retlog/"
        log = readFile(return_log_file_name)
        if log:
            if "End" in log:
                remote_scp1(return_log_file_name, local_log_path)
                # 读取.txt文件
                with open(local_log_path + return_log_file, 'r', encoding='UTF-8') as pfp:
                    # 循环读取每一行的数据
                    for line in pfp.readlines():
                        if "Start to collect" in line:
                            continue
                        elif "End" in line:
                            break
                        else:
                            refreshClusterStatus(line)
                            i.app_opr_result = "集群刷新结果读取完毕"
                            i.save()
            else:
                print("下个定时任务循环读取...")

        else:
            print("无可执行内容")



@shared_task
def appTaskOne(ansible_host_appmgnt_return_filepath,file_name,app_id, app_action, opr_user,applog_id):
    print(app_id)
    print(app_action)
    appTaskTest(ansible_host_appmgnt_return_filepath,file_name,app_id, app_action, opr_user,applog_id)

#检查应用启停结果
@shared_task
def appOprResult():
    applog = CmdbAppLog.objects.filter(app_opr_result="执行中")
    ansible_host_appmgnt_applist_path, ansible_host_appmgnt_return_filepath = get_appmgnt_init_parameter('Ansible')
    for i in applog:
        opr_user = i.app_operation_user
        app_id = i.app_id
        cmdbAppList = CmdbApp.objects.filter(app_id=app_id)
        cmdbApp = cmdbAppList[0]
        file_path_return = ansible_host_appmgnt_return_filepath
        resultfile = opr_user + "_app_oneopr_return_" + i.app_operation + i.app_operation_time.strftime(
            "%Y%m%d%H%M%S") + ".log"
        log = readAppLogFile(ansible_host_appmgnt_return_filepath + resultfile)
        if "正常" in log:
            if i.app_operation == "stop" or i.app_operation == "restart" or i.app_operation == "status":
                cmdbApp.app_status = "1"
                cmdbApp.app_lastopr_result = "成功"
                i.app_opr_result = "成功"
            elif i.app_operation == "stop":
                cmdbApp.app_status = "1"
                cmdbApp.app_lastopr_result = "失败"
                i.app_opr_result = "失败"
        elif "部分正常" in log:
            if i.app_operation == "status":
                cmdbApp.app_status = "2"
                cmdbApp.app_lastopr_result = "成功"
                i.app_opr_result = "成功"
            else:
                cmdbApp.app_status = "2"
                cmdbApp.app_lastopr_result = "失败"
                i.app_opr_result = "失败"
        elif "停止" in log:
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



#逻辑处理，每行数据的处理，task调用 主机状态
def refreshHostStatus(line):
    if line:
        arrayLines = line.split("|")
        cmdbHost = CmdbHost.objects.get(cmdb_host_busip=arrayLines[0])
        cmdbHost.cmdb_host_insert_time = datetime.now()
        if "Falied" in line:
            cmdbHost.cmdb_host_status = "2"
        else:
            cmdbHost.cmdb_host_system = arrayLines[1]
            cmdbHost.cmdb_host_cpu = arrayLines[2]
            cmdbHost.cmdb_host_RAM = arrayLines[3]
            cmdbHost.cmdb_host_local_disc =arrayLines[4]
            cmdbHost.cmdb_host_outlay_disc=arrayLines[5]
            cmdbHost.cmdb_host_status = "1"
        cmdbHost.save()
    else:
        print("此行数据为空！")

#逻辑处理，每行数据的处理，task调用 集群状态
def refreshClusterStatus(line):
    if line:
        arrayLines = line.split(" ")
        appClusterStatus=arrayLines[len(arrayLines)-1]
        appOrClusterName=arrayLines[0]
        #appClusterStatus 为1 为集群 appClusterId为集群id
        #appClusterStatus 为0 为集群 appClusterId为应用id
        if "正常" in line:
            if appClusterStatus == "1\n":
                cmdbAppCluster = CmdbAppCluster.objects.get(name=appOrClusterName)
                cmdbAppCluster.cluster_status = "1"
                cmdbAppCluster.save()
            # 否则是0，为应用
            else:
                cmdbApp = CmdbApp.objects.get(app_name=appOrClusterName)
                cmdbApp.app_status = "1"
                cmdbApp.save()
        elif "部分正常" in line:
            if appClusterStatus=="1\n":
                cmdbAppCluster=CmdbAppCluster.objects.get(name=appOrClusterName)
                cmdbAppCluster.cluster_status="2"
                cmdbAppCluster.save()
            # 否则是0，为应用
            else:
                cmdbApp = CmdbApp.objects.get(app_name=appOrClusterName)
                cmdbApp.app_status= "2"
                cmdbApp.save()
        elif "停止" in line:
            if appClusterStatus=="1\n":
                cmdbAppCluster=CmdbAppCluster.objects.get(name=appOrClusterName)
                cmdbAppCluster.cluster_status="4"
                cmdbAppCluster.save()
            # 否则是0，为应用
            else:
                cmdbApp = CmdbApp.objects.get(app_name=appOrClusterName)
                cmdbApp.app_status= "3"
                cmdbApp.save()
        elif "异常" in line:
            if appClusterStatus == "1\n":
                cmdbAppCluster = CmdbAppCluster.objects.get(name=appOrClusterName)
                cmdbAppCluster.cluster_status = "3"
                cmdbAppCluster.save()
            else:
                print("不存在此状态.....")
    else:
        print("此行数据为空！")
