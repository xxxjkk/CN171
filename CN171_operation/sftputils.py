#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/12/24 14:56
# @Author: zhulong
# @File  : sftputils.py
# @Software: CN171

import os, time
from stat import S_ISDIR as isdir

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from CN171_operation.models import *

# 方法名：目录遍历扫描
# 用途：扫描远端服务器目录，获取需要下载的文件清单
def getFilesListInRemoteHost(sftp, remotedir):
    #保存所有文件名、文件变更时间的列表
    file_list = []
    filemtime_list = []

    #去掉路径字符串最后的字符'/'，如果有的话
    if remotedir[-1] == '/':
        remotedir = remotedir[0:-1]

    #获取当前指定目录下的所有目录及文件，包含属性值
    files = sftp.listdir_attr(remotedir)
    for x in files:
        #remotedir目录中每一个文件或目录的完整路径
        filename = remotedir + '/' + x.filename

        #如果是目录，则递归处理该目录，stat库中的S_ISDIR方法，与linux中的宏的名字完全一致
        if isdir(x.st_mode):
            file_list_extend, filemtime_list_extend = getFilesListInRemoteHost(sftp, filename)
            file_list.extend(file_list_extend)
            filemtime_list.extend(filemtime_list_extend)
        else:
            #判断文件类型
            file_ext = x.filename.split('.')[-1]
            if ('gz' == file_ext):
                file_list.append(filename)
                #获取文件修改时间，用以确认是否存在更新
                filemtime_list.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x.st_mtime)))

    return file_list, filemtime_list


# 方法名：整个目录文件下载
# 用途：下载远端服务器目录下的所有文件，统一下载在本地临时文件夹下（不再创建子目录）
def sftpGetRemoteHostDir(sftp, localdir, remotedir, **kwargs):
    if kwargs['type'] == 'Finance_BDI':
        #如果入参包含下载文件列表，则以入参列表为准进行下载
        file_list = kwargs['dfile_list']
        filemtime_list = kwargs['dfilemtime_list']
        isnew_list = kwargs['disnew_list']
        type_list = kwargs['dtype_list']
    else:
        #获取远端服务器上指定目录及其子目录下的所有文件
        file_list = getFilesListInRemoteHost(sftp, remotedir)

    print(u'开始下载%s目录下的所有文件：共计%s个' %(remotedir,len(file_list)))
    result = []
    #依次下载每个文件
    for x in range(len(file_list)):
        filename = file_list[x].split('/')[-1]
        localfilename = os.path.join(localdir, filename)
        try:
            print(u'下载文件%s中...' %file_list[x])
            sftp.get(file_list[x], localfilename)
            result.append('成功')
        except Exception as e:
            result.append(filename)

        #若为账务文件，则进行数据入库
        if kwargs['type'] == 'Finance_BDI':
            #针对是否新下载文件或更新文件做不同处理
            if isnew_list[x] == 'yes':
                #若为新文件，先不插入外键数据，下载到临时文件夹，待文件整理时进行统一外键赋值
                fileinstance = OprFinanceFiledetail()
                fileinstance.opr_finance_filedetail_name = filename
                fileinstance.opr_finance_filedetail_type = type_list[x]
                fileinstance.opr_finance_filedetail_createtime = filemtime_list[x]
                fileinstance.opr_finance_filedetail_thistime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                fileinstance.opr_finance_filedetail_num = 1
                fileinstance.opr_finance_filedetail_check = '尚未校验'
                fileinstance.opr_finance_filedetail_dir = localdir
                fileinstance.save()
            elif isnew_list[x] == 'no':
                try:
                    fileinstance = OprFinanceFiledetail.objects.get(opr_finance_filedetail_name = filename)
                except ObjectDoesNotExist:
                    print(u'文件%s数据未入库，不进行处理！' %filename)
                    continue
                except MultipleObjectsReturned:
                    print(u'文件%s存在多条相同数据，存在异常，不进行处理！' %filename)
                    continue
                fileinstance.opr_finance_filedetail_createtime = filemtime_list[x]
                fileinstance.opr_finance_filedetail_lasttime = fileinstance.opr_finance_filedetail_thistime
                fileinstance.opr_finance_filedetail_thistime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                fileinstance.opr_finance_filedetail_num += 1
                fileinstance.opr_finance_filedetail_dir = localdir
                fileinstance.save()

    file_fail_list = list(filter(lambda s: s.find('成功'), result))
    if file_fail_list:
        print(u'部分文件下载失败，文件名为：')
        for file in file_fail_list:
            print(file)
    else:
        print(u'文件全部下载成功！')

    return file_fail_list


# 方法名：目录遍历扫描
# 用途：扫描远端服务器目录，获取需要下载的文件清单
def getFilesListInLocalHost(localdir):
    #保存所有文件名、文件变更时间的列表
    file_list = []

    #去掉路径字符串最后的字符'/'，如果有的话
    if localdir[-1] == '/':
        remotedir = localdir[0:-1]

    #获取当前指定目录下的所有目录及文件，包含属性值
    files = os.listdir(localdir)
    for x in files:
        #localdir目录中每一个文件或目录的完整路径
        filename = os.path.join(localdir, x.filename)

        #如果是目录，则递归处理该目录，stat库中的S_ISDIR方法，与linux中的宏的名字完全一致
        if os.path.isdir(x):
            file_list.extend(getFilesListInLocalHost(filename))
        else:
            #判断文件类型
            file_ext = x.filename.split('.')[-1]
            if ('gz' == file_ext):
                file_list.append(filename)
    return file_list

# 方法名：整个目录文件上传
# 用途：上传本地目录下的所有文件到远端服务器目录下
def sftpPutRemoteHostDir(sftp, sshd, localdir, remotedir, **kwargs):
    if kwargs['type'] == 'Finance_BDI':
        #如果入参包含文件列表，则以入参列表为准进行上传
        file_list = kwargs['filelist']
        print('file_list :',file_list)
    else:
        #获取远端服务器上指定目录及其子目录下的所有文件
        file_list = getFilesListInLocalHost(localdir)

    if remotedir[-1] == '/':
        remotedir = remotedir[0:1]

    print(u'开始上传文件：共计%s个' % len(file_list))
    result = []
    remotefiledir_list = []
    #依次上传每个文件
    for file in file_list:
        filename = file.replace('\\\\', '/').split('cmiot_finance/')[-1]
        remotefilename = os.path.join(remotedir, filename)
        remotefilename = remotefilename.replace('\\', '/')
        remotefiledir = remotefilename[::-1].split('/', 1)[-1][::-1]

        if remotefiledir not in remotefiledir_list:
            print(u'新建稽核服务器目录：%s' %remotefiledir)
            cmd = 'mkdir -p ' + remotefiledir
            stdin, stdout, stderr = sshd.exec_command(cmd)
            err_list = stderr.readlines()
            if len(err_list) > 0:
                print('创建目录失败，失败原因为:', err_list[0])
            else:
                #创建完成后，在列表中记录，避免重复操作，浪费时间
                remotefiledir_list.append(remotefiledir)
        try:
            print(u'上传文件\'%s\'中...' %filename)
            sftp.put(file, remotefilename)
            result.append('成功')
        except Exception as e:
            print(e)
            result.append(file.replace('\\\\', '\\'))

    file_fail_list = list(filter(lambda s: s.find('成功'), result))
    if file_fail_list:
        print(u'部分文件上传失败，文件名为：')
        for file in file_fail_list:
            print(file)
    else:
        print(u'文件全部上传成功！')

    return file_fail_list