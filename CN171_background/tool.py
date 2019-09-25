#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/9/25 15:22
# @Author: zhaocy
# @File  : tool.py.py
# @Software: CN171

import sys
import paramiko


# 连接构建服务器
def ssh_connect():
    hostname = '39.104.61.178'
    username = 'zhaocy'
    password = 'zcY!123456'
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


# 启动应用
def app_start(ip, user, app_type, exec_cmd):
    if app_type == 'jdk':
        cmd = "ansible %s -u %s -m shell -a 'source ~/.bash_profile && cd $BIN_HOME && sh %s'" \
              % (ip, user, exec_cmd)
    elif app_type == 'tomcat':
        cmd = "ansible %s -u %s -m shell -a 'source ~/.bash_profile && cd $BIN_HOME/.. && nohup ./bin/startup.sh'" \
              % (ip, user)
    else:
        sys.exit(0)

    sshd = ssh_connect()
    stdin, stdout, stderr = ssh_exec_cmd(sshd, cmd)
    err_list = stderr.readlines()

    if len(err_list) > 0:
        print('Start failed:' + err_list[0])
        sys.exit(0)
    else:
        print('Start success.')

    for item in stdout.readlines():
        print(item)

    ssh_close(sshd)


# 停止应用
def app_stop(ip, user):
    cmd = """ansible %s -u %s -m shell -a 'ps x|grep java|grep -v grep|cut -d " " -f 1|xargs kill -9'""" \
          % (ip, user)
    sshd = ssh_connect()
    stdin, stdout, stderr = ssh_exec_cmd(sshd, cmd)
    err_list = stderr.readlines()

    if len(err_list) > 0:
        print('Stop failed: ' + err_list[0])
        sys.exit(0)
    else:
        print('Stop success.')

    for item in stdout.readlines():
        print(item)

    ssh_close(sshd)


# 测试1 netty或者spring非tomcat的应用启动方法
# app_start(ip='192.168.250.103', user='pay_str', app_type='jdk', exec_cmd='start.sh 172.28.250.242 172.28.250.142')

# 测试2 tomcat的应用启动方法
# app_start(ip='192.168.250.103', user='client_str', app_type='tomcat', exec_cmd='')

# 测试3 停止应用的方法
# app_stop(ip='192.168.250.103', user='client_str')

