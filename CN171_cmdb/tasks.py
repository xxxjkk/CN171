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
from CN171_cmdb.models import CmdbHost
from CN171_tools.connecttool import remote_scp, readFile, ssh_connect, ssh_exec_cmd, get_hostmgnt_init_parameter
from CN171_tools.sftputils import remote_scp1

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


def local_log_path(args):
    pass


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



#逻辑处理，每行数据的处理，task调用
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


