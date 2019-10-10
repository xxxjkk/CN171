#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/10/9 14:16
# @Author: zhulong
# @File  : sftputils.py
# @Software: CN171

import os
import paramiko
from django.shortcuts import render

try:
    import ConfigParser as cp
except ImportError as e:
    import configparser as cp

#读取配置文件
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = cp.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config/cn171.conf'))

#PBOSS文件路径和备份路径
pboss_remotefiledir = config.get('PBOSS', 'pboss_order_remote_filedir')
pboss_remotefilebakdir = config.get('PBOSS', 'pboss_order_remote_filedirbak')
pboss_localfiledir = config.get('PBOSS', 'pboss_order_local_filedir')
pboss_localfilebakdir = config.get('PBOSS', 'pboss_order_local_filedirbak')


#sFTP连接初始化
def sftpconnect(type):
    if type == "PBOSS":
        # PBOSS主机配置
        pboss_host = config.get('PBOSS', 'pboss_order_host')
        pboss_port = config.get('PBOSS', 'pboss_order_port')
        pboss_user = config.get('PBOSS', 'pboss_order_user')
        pboss_password = config.get('PBOSS', 'pboss_order_password')

        t = paramiko.Transport(sock=(pboss_host,int(pboss_port)))
        t.connect(username=pboss_user, password=pboss_password)
    elif type == "CMIOT":
        # CMIOT主机配置
        cmiot_host = config.get('Ansible', 'ansible_host')
        cmiot_port = config.get('Ansible', 'ansible_port')
        cmiot_user = config.get('Ansible', 'ansible_user')
        cmiot_password = config.get('Ansible', 'ansible_password')

        t = paramiko.Transport(sock=(cmiot_host,int(cmiot_port)))
        t.connect(username=cmiot_user, password=cmiot_password)
    sftp = paramiko.SFTPClient.from_transport(t)
    return sftp

#sFTP文件下载
def filedownload(sftp_file_path, sftp_filebak_path, dst_file_path):
    #获取sftp连接
    sftp = sftpconnect("PBOSS")

    #获取目标地址文件清单
    file_list = sftp.listdir(sftp_file_path)

    for file in file_list:
        # 判断是否为xlsx的Excel文件
        file_ext = file.split('.')[1]
        if 'xlsx' == file_ext:
            sftp_file = os.path.join(sftp_file_path, file)
            sftp_filebak = os.path.join(sftp_filebak_path, file)
            dst_file = os.path.join(dst_file_path, file)
            print("远程文件：" + sftp_file)

            #判断本地是否存在同名文件
            if os.path.exists(dst_file):
                print("文件《" + file + "》在本地目录已存在，暂不下载！")
            else:
                #下载文件
                sftp.get(sftp_file, dst_file)
                #移动文件
                sftp.rename(oldpath=sftp_file, newpath=sftp_filebak)
                print("文件《" + file + "》下载完成！")

def sftptest(request):
    print("FTP test...........")
    filedownload(sftp_file_path=pboss_remotefiledir, sftp_filebak_path=pboss_remotefilebakdir, dst_file_path=pboss_localfiledir)

    return render(request, "order/test.html")
