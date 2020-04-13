#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/10/9 14:16
# @Author: zhulong
# @File  : sftputils.py
# @Software: CN171

import os
import paramiko
from django.shortcuts import render
from CN171_tools.connecttool import ssh_connect,ssh_exec_cmd,ssh_close

try:
    import ConfigParser as cp
except ImportError as e:
    import configparser as cp

#读取配置文件
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = cp.RawConfigParser()
config.read(os.path.join(BASE_DIR, 'config/cn171.conf'),encoding='utf-8')

#PBOSS文件路径和备份路径
pboss_remotefiledir = config.get('PBOSS', 'pboss_order_remote_filedir')
pboss_remotefilebakdir = config.get('PBOSS', 'pboss_order_remote_filedirbak')
pboss_localfiledir = config.get('PBOSS', 'pboss_order_local_filedir')
pboss_localfilebakdir = config.get('PBOSS', 'pboss_order_local_filedirbak')


#sFTP连接初始化
def sftpconnect(type, **kwargs):
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
        cmiot_host = config.get('Ansible', 'ansible_host_host')
        cmiot_port = config.get('Ansible', 'ansible_host_port')
        cmiot_user = config.get('Ansible', 'ansible_host_user')
        cmiot_password = config.get('Ansible', 'ansible_host_password')

        t = paramiko.Transport(sock=(cmiot_host,int(cmiot_port)))
        t.connect(username=cmiot_user, password=cmiot_password)

    elif type == "Finance_BDI":
        #Finance_BDI主机配置
        finance_host = kwargs['host']
        finance_port = kwargs['port']
        finance_user = kwargs['user']
        finance_password = kwargs['passwd']

        t = paramiko.Transport(sock=(finance_host,int(finance_port)))
        t.connect(username=finance_user, password=finance_password)
    else:
        print(type + "not find!")
        exit()

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
#sftp 为sftp连接句柄，local 本地文件绝对路径（包含文件名），服务器端路径（不含文件名）
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


#从远程机器上下载文件（夹）到本地
from stat import S_ISDIR as isdir
def _check_local(local):
    if not os.path.exists(local):
        try:
            os.mkdir(local)
        except IOError as err:
            print(err)

def get(sftp,remote,local):
    #检查远程文件是否存在
    try:
        result = sftp.stat(remote)
    except IOError as err:
        error = '[ERROR %s] %s: %s' %(err.errno,os.path.basename(os.path.normpath(remote)),err.strerror)
        print(error)
    else:
        #判断远程文件是否为目录
        if isdir(result.st_mode):
            dirname = os.path.basename(os.path.normpath(remote))
            local = os.path.join(local,dirname)
            _check_local(local)
            for file in sftp.listdir(remote):
                sub_remote = os.path.join(remote,file)
                sub_remote = sub_remote.replace('\\','/')
                get(sftp,sub_remote,local)
        else:
        #拷贝文件
            if os.path.isdir(local):
                local = os.path.join(local,os.path.basename(remote))
            try:
                sftp.get(remote,local)
            except IOError as err:
                print(err)
            else:
                print('[get]',local,'<==',remote)


#远程下载文件
#remote_path_file 带绝对路径的文件名  local_path 本地路径
def remote_scp1(remote_path_file,local_path):
    t, sftp = sftpconnect("CMIOT")
    try:
        get(sftp,remote_path_file, local_path)
        t.close()
        sshd = ssh_connect("Ansible")
        #获得该文件后直接删除该文件，而不是删除该目录下的文件
        cmd = "rm -f " + remote_path_file
        ssh_exec_cmd(sshd, cmd)
        ssh_close(sshd)
    except IOError:
        print("not exist")


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
