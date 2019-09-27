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
def ssh_connect():
    hostname = config.get('Ansible', 'ansible_host')
    username = config.get('Ansible', 'ansible_user')
    password = config.get('Ansible', 'ansible_password')
    try:
        ssh_fd = paramiko.SSHClient()
        ssh_fd.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_fd.connect(hostname, username=username, password=password)
        return ssh_fd
    except Exception as e:
        print('ssh %s@%s: %s' % (username, hostname, e))
        exit()


# 远程执行命令方法
def ssh_exec_cmd(ssh_fd, cmd):
    return ssh_fd.exec_command(cmd)


# 关闭ssh连接
def ssh_close(ssh_fd):
    ssh_fd.close()


# 单个中心执行函数
def domainExecuteOne(exec_cmd):
    sshd = ssh_connect()
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

