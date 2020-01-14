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
from CN171_cmdb.models import CmdbHost, CmdbApp, CmdbAppCluster, CLUSTER_STATUS, APP_STATUS
from CN171_tools.common_api import get_tuple_key
from CN171_tools.connecttool import remote_scp, readFile, ssh_connect, ssh_exec_cmd, get_hostmgnt_init_parameter, \
    get_appmgnt_cluster_init_parameter
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
def batchRefreshClusterStatusTask(ansible_cmdb_appmgnt_clusterReturn_filepath,user_name):
    returnmsg = "False"
    file_path_return = ansible_cmdb_appmgnt_clusterReturn_filepath
    file_name_return = user_name+"_refresh_cluster_status_return"
    conntarget = "Ansible"
    sshd = ssh_connect(conntarget)
    dir_cmd = "mkdir "+ file_path_return
    ssh_exec_cmd(sshd, dir_cmd)
    cmd = "./clusterManagement.sh status" + " >> " + file_path_return + "/" + file_name_return + ".log"
    stdin, stdout, stderr = ssh_exec_cmd(sshd, cmd)
    err_list = stderr.readlines()
    if len(err_list) > 0:
        print('Refresh failed:' + err_list[0])
    else:
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
    local_log_path="temp/cmdb/hostmgnt/status/retlog/"
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

#异步查询主机状态结果
@shared_task
def checkClusterStatusResult():
    #返回的日志文件名
    return_log_file=request.session.get('user_name')+"_refresh_cluster_status_return.log"
    #获取返回的文件路径
    ansible_cmdb_appmgnt_appClusterlist_path, ansible_cmdb_appmgnt_clusterReturn_filepath = get_appmgnt_cluster_init_parameter('Ansible')

    #返回文件的带绝对路径的文件
    return_log_file_name = ansible_cmdb_appmgnt_clusterReturn_filepath+return_log_file
    #返回文件写入本地的目录
    local_log_path="temp/cmdb/appmgnt/cluster/status/retlog/"
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
                        refreshClusterStatus(line)
        else:
            print("下个定时任务循环读取...")
    else:
        print("无可执行内容")

@shared_task
def appTaskOne(ansible_host_appmgnt_return_filepath,file_name,app_id, app_action, opr_user):
    cmdbApp = CmdbApp.objects.get(app_id=app_id)
    file_path_return = ansible_host_appmgnt_return_filepath
    file_name_return = opr_user + "_app_oneopr_return"
    conntarget = "Ansible"
    sshd = ssh_connect(conntarget)
    dir_cmd = "mkdir " + file_path_return
    ssh_exec_cmd(sshd, dir_cmd)
    cmd = "aaa.sh "+file_name+" action=" +app_action+ " |tee -a " + file_path_return  + file_name_return + ".log"
    stdin, stdout, stderr = ssh_exec_cmd(sshd, cmd)
    err_list = stderr.readlines()
    if len(err_list) > 0:
        print('Start failed:' + err_list[0])
        returnmsg = "False"
        if app_action != 'status':
            cmdbApp.bg_lastopr_result = "失败"
            cmdbApp.save()
    else:
        print('Start success.')
        returnmsg = "True"
    sshd.close()
    return returnmsg


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
        appClusterStatus=arrayLines[len(arrayLines)-2]
        appClusterId=arrayLines[len(arrayLines)-1]
        #appClusterStatus 为1 为集群 appClusterId为集群id
        #appClusterStatus 为0 为集群 appClusterId为应用id
        if "Falied" in line:
            if appClusterStatus==1:
                cmdbAppCluster=CmdbAppCluster.objects.get(id=appClusterId)
                cmdbAppCluster.cluster_status="3"
                cmdbAppCluster.save()
            # 否则是0，为应用
            else:
                cmdbApp = CmdbApp.objects.get(app_id=appClusterId)
                cmdbApp.app_status="3"
                cmdbApp.save()
        else:
            if appClusterStatus==1:
                cmdbAppCluster=CmdbAppCluster.objects.get(id=appClusterId)
                cmdbAppCluster.cluster_status=get_tuple_key(CLUSTER_STATUS,arrayLines[3])
                cmdbAppCluster.save()
            # 否则是0，为应用
            else:
                cmdbApp = CmdbApp.objects.get(app_id=appClusterId)
                cmdbApp.app_status=get_tuple_key(APP_STATUS,arrayLines[2])
                cmdbApp.save()
    else:
        print("此行数据为空！")
