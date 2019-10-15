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
    return t, sftp

#连接关闭
def sftpDisconnect(client):
    try:
        if client:
            client.close()
    except Exception as e:
        print(e)

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

#本地文件拷贝到远程
def put(sftp,local,remote):
    #检查路径是否存在
    def _is_exists(path,function):
        path = path.replace('\\','/')
        try:
            function(path)
        except Exception as error:
            return False
        else:
            return True
    #拷贝文件
    def _copy(sftp,local,remote):
        #判断remote是否是目录
        if _is_exists(remote,function=sftp.chdir):
            #是，获取local路径中的最后一个文件名拼接到remote中
            filename = os.path.basename(os.path.normpath(local))
            remote = os.path.join(remote,filename).replace('\\','/')
        #如果local为目录
        if os.path.isdir(local):
            #在远程创建相应的目录
            _is_exists(remote,function=sftp.mkdir)
            #遍历local
            for file in os.listdir(local):
                #取得file的全路径
                localfile = os.path.join(local,file).replace('\\','/')
                #深度递归_copy()
                _copy(sftp=sftp,local=localfile,remote=remote)
        #如果local为文件
        if os.path.isfile(local):
            try:
                sftp.put(local,remote)
            except Exception as error:
                print(error)
                print('[put]',local,'==>',remote,'FAILED')
                return False
            else:
                print('[put]',local,'==>',remote,'SUCCESSED')
                return True
    #检查local
    if not _is_exists(local,function=os.stat):
        print("'"+local+"': No such file or directory in local")
        return False
    #检查remote的父目录
    remote_parent =  os.path.dirname(os.path.normpath(remote))
    if not _is_exists(remote_parent,function=sftp.chdir):
        print("'"+remote+"': No such file or directory in remote")
        return False
    #拷贝文件
    flag=_copy(sftp=sftp,local=local,remote=remote)
    return flag

def sftp_upload(sftp,local,remote):
    try:
        if os.path.isdir(local):#判断本地参数是目录还是文件
            for f in os.listdir(local):#遍历本地目录
                sftp.put(os.path.join(local+f),os.path.join(remote+f))#上传目录中的文件
        else:
            sftp.put(local,remote)#上传文件
        return True
    except Exception as e:
        print('upload exception:',e)
        return False
#判断filePath目录不存在则创建
def path_not_exist_create(filePath):
    try:
        if not os.path.exists(filePath):
            os.makedirs(filePath, 0o777)
    except Exception as e:
        print('create exception:',e)

def sftptest(request):
    print("FTP test...........")
    filedownload(sftp_file_path=pboss_remotefiledir, sftp_filebak_path=pboss_remotefilebakdir, dst_file_path=pboss_localfiledir)

    return render(request, "order/test.html")
