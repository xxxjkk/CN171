#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/9/26 14:55
# @Author: zhulong
# @File  : connecttool.py
# @Software: CN171

import sys
import os
import paramiko
try:
    import ConfigParser as cp
except ImportError as e:
    import configparser as cp

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = cp.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config/cn171.conf'))


# 连接构建服务器
def ssh_connect(conntarget):
    if conntarget == "Ansible":
        hostname = config.get('Ansible', 'ansible_host')
        username = config.get('Ansible', 'ansible_user')
        password = config.get('Ansible', 'ansible_password')
    elif conntarget == "PBOSS":
        hostname = config.get('PBOSS', 'pboss_order_host')
        username = config.get('PBOSS', 'pboss_order_user')
        password = config.get('PBOSS', 'pboss_order_password')
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
    if conntarget == "Ansible":
        hostname = config.get('Ansible', 'ansible_host')
        port=config.get('Ansible','ansible_port')
        username = config.get('Ansible', 'ansible_user')
        password = config.get('Ansible', 'ansible_password')
    elif conntarget == "PBOSS":
        hostname = config.get('PBOSS', 'pboss_order_host')
        port=config.get('PBOSS','pboss_order_port')
        username = config.get('PBOSS', 'pboss_order_user')
        password = config.get('PBOSS', 'pboss_order_password')
    else:
        print(conntarget + "not find!")
        exit()
    return hostname, port, username, password

def get_init_parameter1(conntarget):
    if conntarget == "Ansible":
        ansible_general_host_pwd = config.get('Ansible', 'ansible_general_host_pwd')
        ansible_root_host_pwd=config.get('Ansible','ansible_root_host_pwd')
    elif conntarget == "PBOSS":
        ansible_general_host_pwd = config.get('PBOSS', 'ansible_general_host_pwd')
        ansible_root_host_pwd = config.get('PBOSS', 'ansible_root_host_pwd')
    else:
        print(conntarget + "not find!")
        exit()
    return ansible_general_host_pwd, ansible_root_host_pwd

def get_init_parameter2(conntarget):
    if conntarget == "Ansible":
        remote_path = config.get('Ansible', 'remote_path')
    elif conntarget == "PBOSS":
        remote_path = config.get('PBOSS', 'remote_path')
    else:
        print(conntarget + "not find!")
        exit()
    return remote_path