#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/9/26 14:55
# @Author: zhulong
# @File  : connecttool.py
# @Software: CN171
import re
import sys
import os
from functools import reduce

import paramiko
try:
    import ConfigParser as cp
except ImportError as e:
    import configparser as cp

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = cp.RawConfigParser()
config.read(os.path.join(BASE_DIR, 'config/cn171.conf'),encoding='utf-8')


# 连接构建服务器
def ssh_connect(conntarget):
    if conntarget == "Ansible_bg":
        hostname = config.get('Ansible_bg', 'ansible_bg_host')
        username = config.get('Ansible_bg', 'ansible_bg_user')
        password = config.get('Ansible_bg', 'ansible_bg_password')
    elif conntarget == "PBOSS":
        hostname = config.get('PBOSS', 'pboss_order_host')
        username = config.get('PBOSS', 'pboss_order_user')
        password = config.get('PBOSS', 'pboss_order_password')
    elif conntarget == "Ansible":
        hostname = config.get('Ansible', 'ansible_host')
        username = config.get('Ansible', 'ansible_user')
        password = config.get('Ansible', 'ansible_password')
    elif conntarget == "Finance_BDI":
        config.read(os.path.join(BASE_DIR, 'config/operation.conf'), encoding='utf-8')
        hostname = config.get('Finance', 'finance_bdihostip')
        username = config.get('Finance', 'finance_bdihostuser')
        password = config.get('Finance', r'finance_bdihostpasswd')
    elif conntarget == "Finance_Reco":
        config.read(os.path.join(BASE_DIR, 'config/operation.conf'), encoding='utf-8')
        hostname = config.get('Finance', 'finance_financehostip')
        username = config.get('Finance', 'finance_financehostuser')
        password = config.get('Finance', r'finance_financehostpasswd')
    else:
        print(conntarget + "not find!")
        exit()
    try:
        ssh_fd = paramiko.SSHClient()
        ssh_fd.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_fd.connect(hostname, username=username, password=password)
        return ssh_fd
    except Exception as e:
        print('ssh %s@%s: %s' % (username, hostname, e))
        exit()

#建立与客户机通道，并激活shell终端
def build_shell_channel(conntarget):
    hostname, port, username, password=get_init_parameter(conntarget)
    try:
        trans=paramiko.Transport((hostname, 22))
        trans.start_client()
        # 用户名密码方式
        trans.auth_password(username, password)
        # 打开一个通道
        channel = trans.open_session()
        channel.settimeout(7200)
        # 获取一个终端
        channel.get_pty()
        # 激活器
        channel.invoke_shell()
    except Exception as e:
        print(e)
    return trans, channel

#关闭远程客户机的shell终端和channel通道
def close_shell_channel(trans, channel):
    if channel:
        channel.close()
    if trans:
        trans.close()

# 远程执行命令方法
def ssh_exec_cmd(ssh_fd, cmd):
    return ssh_fd.exec_command(cmd)


# 关闭ssh连接
def ssh_close(ssh_fd):
    ssh_fd.close()


# 单个中心执行函数
def domainExecuteOne(exec_cmd):
    conntarget = "Ansible"
    sshd = ssh_connect(conntarget)
    stdin, stdout, stderr = ssh_exec_cmd(sshd, exec_cmd)
    err_list = stderr.readlines()
    if len(err_list) > 0:
        print('Start failed:' + err_list[0])
        sys.exit(0)
    else:
        print('Start success.')
    for item in stdout.readlines():
        print(item)
    ssh_close(sshd)


#PBOSS订单生成函数
def pbossOrderMake(type):
    conntarget = "PBOSS"
    sshd = ssh_connect(conntarget)
    script = config.get('PBOSS', 'pboss_order_script')

    #根据不同类型执行不同的生成命令
    if type == 'status':
        exec_cmd = config.get('PBOSS', 'pboss_order_status_script')
    elif type == 'node':
        exec_cmd = config.get('PBOSS', 'pboss_order_node_script')
    elif type == 'rollback':
        exec_cmd = config.get('PBOSS', 'pboss_order_rollback_script')
    else:
        print("未找到对应类型！")
        return "失败"

    stdin, stdout, stderr = ssh_exec_cmd(sshd, exec_cmd)
    err_list = stderr.readlines()
    if len(err_list) > 0:
        print('Start failed:' + err_list[0])
        return "失败"
    else:
        print('Start success.')
    for item in stdout.readlines():
        print(item)
    ssh_close(sshd)
    return "成功"

def get_init_parameter(conntarget):
    if conntarget == "Ansible_bg":
        hostname = config.get('Ansible', 'ansible_bg_host')
        port=config.get('Ansible','ansible_bg_port')
        username = config.get('Ansible', 'ansible_bg_user')
        password = config.get('Ansible', 'ansible_bg_password')
    elif conntarget == "PBOSS":
        hostname = config.get('PBOSS', 'pboss_order_host')
        port=config.get('PBOSS','pboss_order_port')
        username = config.get('PBOSS', 'pboss_order_user')
        password = config.get('PBOSS', 'pboss_order_password')
    elif conntarget == "Ansible":
        hostname = config.get('Ansible', 'ansible_host_host')
        port = config.get('Ansible', 'ansible_host_port')
        username = config.get('Ansible', 'ansible_host_user')
        password = config.get('Ansible', 'ansible_host_password')
    else:
        print(conntarget + "not find!")
        exit()
    return hostname, port, username, password

def get_init_parameter1(conntarget):
    if conntarget == "Ansible":
        ansible_host_pwmgnt_login_pwd = config.get('Ansible', 'ansible_host_pwmgnt_login_pwd')
        ansible_host_pwmgnt_root_pwd=config.get('Ansible','ansible_host_pwmgnt_root_pwd')
    elif conntarget == "PBOSS":
        ansible_host_pwmgnt_login_pwd = config.get('PBOSS', 'ansible_host_pwmgnt_login_pwd')
        ansible_host_pwmgnt_root_pwd = config.get('PBOSS', 'ansible_host_pwmgnt_root_pwd')
    else:
        print(conntarget + "not find!")
        exit()
    return ansible_host_pwmgnt_login_pwd, ansible_host_pwmgnt_root_pwd

def get_init_parameter2(conntarget):
    if conntarget == "Ansible":
        ansible_host_pwmgnt_ipfile_path = config.get('Ansible', 'ansible_host_pwmgnt_ipfile_path')
    elif conntarget == "PBOSS":
        ansible_host_pwmgnt_ipfile_path = config.get('PBOSS', 'ansible_host_pwmgnt_ipfile_path')
    else:
        print(conntarget + "not find!")
        exit()
    return ansible_host_pwmgnt_ipfile_path

#主机管理刷新状态功能，得到初始化参数
def get_hostmgnt_init_parameter(conntarget):
    if conntarget == "Ansible":
        ansible_host_hostmgnt_busiip_path = config.get('Ansible', 'ansible_host_hostmgnt_busiip_path')
        ansible_host_hostmgnt_return_filepath = config.get('Ansible', 'ansible_host_hostmgnt_return_filepath')
        ansible_host_hostmgnt_scrideploy_path = config.get('Ansible', 'ansible_host_hostmgnt_scrideploy_path')
    elif conntarget == "PBOSS":
        ansible_host_hostmgnt_busiip_path = config.get('Ansible', 'ansible_host_hostmgnt_busiip_path')
        ansible_host_hostmgnt_return_filepath = config.get('Ansible', 'ansible_host_hostmgnt_return_filepath')
        ansible_host_hostmgnt_scrideploy_path = config.get('Ansible', 'ansible_host_hostmgnt_scrideploy_path')
    else:
        print(conntarget + "not find!")
        exit()
    return ansible_host_hostmgnt_busiip_path,ansible_host_hostmgnt_return_filepath,ansible_host_hostmgnt_scrideploy_path


#应用管理刷新集群状态功能，得到初始化参数
def get_appmgnt_cluster_init_parameter(conntarget):
    if conntarget == "Ansible":
        ansible_cmdb_appmgnt_appClusterlist_path = config.get('Ansible', 'ansible_cmdb_appmgnt_appClusterlist_path')
        ansible_cmdb_appmgnt_clusterReturn_filepath = config.get('Ansible', 'ansible_cmdb_appmgnt_clusterReturn_filepath')
    elif conntarget == "PBOSS":
        ansible_cmdb_appmgnt_appClusterlist_path = config.get('Ansible', 'ansible_cmdb_appmgnt_appClusterlist_path')
        ansible_cmdb_appmgnt_clusterReturn_filepath = config.get('Ansible', 'ansible_cmdb_appmgnt_clusterReturn_filepath')
    else:
        print(conntarget + "not find!")
        exit()
    return ansible_cmdb_appmgnt_appClusterlist_path,ansible_cmdb_appmgnt_clusterReturn_filepath

#应用管理主机操作（启动、停止、重启、刷新），得到初始化参数
def get_appmgnt_init_parameter(conntarget):
    if conntarget == "Ansible":
        ansible_host_appmgnt_applist_path = config.get('Ansible', 'ansible_host_appmgnt_applist_path')
        ansible_host_appmgnt_return_filepath = config.get('Ansible', 'ansible_host_appmgnt_return_filepath')
        #ansible_host_appmgnt_scrideploy_path = config.get('Ansible', 'ansible_host_appmgnt_scrideploy_path')
    elif conntarget == "PBOSS":
        ansible_host_appmgnt_applist_path = config.get('Ansible', 'ansible_host_appmgnt_applist_path')
        ansible_host_appmgnt_return_filepath = config.get('Ansible', 'ansible_host_appmgnt_return_filepath')
        #ansible_host_appmgnt_scrideploy_path = config.get('Ansible', 'ansible_host_appmgnt_scrideploy_path')
    else:
        print(conntarget + "not find!")
        exit()
    return ansible_host_appmgnt_applist_path,ansible_host_appmgnt_return_filepath


def readFile(file_path):
    exec_cmd = "cat "+ file_path
    log_msg = ""
    sshd = ssh_connect("Ansible_bg")
    stdin, stdout, stderr = ssh_exec_cmd(sshd, exec_cmd)
    err_list = stderr.readlines()
    if len(err_list) > 0:
        print('Read failed:' + err_list[0])
        sys.exit(0)
    else:
        print('Start success.')
        for item in stdout.readlines():
            log_msg = log_msg + item
        return log_msg
    ssh_close(sshd)

#读取app操作结果日志
def readAppLogFile(file_path):
    exec_cmd = "cat "+ file_path
    log_msg = ""
    sshd = ssh_connect("Ansible")
    stdin, stdout, stderr = ssh_exec_cmd(sshd, exec_cmd)
    err_list = stderr.readlines()
    if len(err_list) > 0:
        print('Read failed:' + err_list[0])
        sys.exit(0)
    else:
        print('Start success.')
        for item in stdout.readlines():
            log_msg = log_msg + item
        return log_msg
    ssh_close(sshd)

#远程下载文件
def remote_scp(remote_path,local_path):
    hostname, port, username, password = get_init_parameter("Ansible_bg")
    port = str2int(port)
    t = paramiko.Transport((hostname, port))
    t.connect(username=username, password=password)  # 登录远程服务器
    sftp = paramiko.SFTPClient.from_transport(t)  # sftp传输协议
    src = remote_path
    des = local_path
    #log_dir_name = src.split("/")
    # 适配Linux环境，截取日志文件名
    if '/' in src:
        log_dir_name = src.split('/')[-1]
    # 适配Windows环境，截取日志文件名
    elif '\\' in src:
        log_dir_name = src.split('\\')[-1]
    else:
        response = "Log file not exits!"
        return response
    #a = len(log_dir_name)
    downfilename = log_dir_name
    dir_name = str(downfilename)
    try:
        sftp.get(src, des)
        t.close()
        sshd = ssh_connect("Ansible_bg")
        dir_del_name = dir_name.split('.')[0]
        cmd = "rm -rf " +dir_del_name
        ssh_exec_cmd(sshd, cmd)
        ssh_close(sshd)
    except IOError:
        print("not exist")

#远程下载文件不删除
def sftpScp(remote_path,local_path):
    hostname, port, username, password = get_init_parameter("Ansible")
    port = str2int(port)
    t = paramiko.Transport((hostname, port))
    t.connect(username=username, password=password)  # 登录远程服务器
    sftp = paramiko.SFTPClient.from_transport(t)  # sftp传输协议
    src = remote_path
    des = local_path
    #log_dir_name = src.split("/")
    # 适配Linux环境，截取日志文件名
    if '/' in src:
        log_dir_name = src.split('/')[-1]
    # 适配Windows环境，截取日志文件名
    elif '\\' in src:
        log_dir_name = src.split('\\')[-1]
    else:
        response = "Log file not exits!"
        return response
    #a = len(log_dir_name)
    downfilename = log_dir_name
    dir_name = str(downfilename)
    try:
        flag = sftp.get(src, des)
        t.close()
    except IOError:
        print("not exist")
    return flag

def str2int(s):
    def fn(x,y):
        return x*10+y
    def char2num(s):
        return {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9}[s]
    return reduce(fn,map(char2num,s))