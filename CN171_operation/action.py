#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/12/19 16:04
# @Author: zhulong
# @File  : action.py
# @Software: CN171

import datetime, re
import sys

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Count
from django.core.cache import cache

from CN171_operation.sftputils import *
from CN171_operation.models import *
from CN171_operation.finance.filesclassify import filesClassify
from CN171_tools.sftputils import *

try:
    import ConfigParser as cp
except ImportError as e:
    import configparser as cp

#读取配置文件
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = cp.RawConfigParser()
config.read(os.path.join(BASE_DIR, 'config/operation.conf'),encoding='utf-8')


#CMIOT账务文件管理页面——BDI服务器文件下载方法
def cFinanceFileDownload():
    print('开始下载MDS主机的账务文件...........')

    #获取MDS主机IP列表、端口、账号信息
    hostip_list = config.get('Finance', 'finance_bdihostip').split(', ')
    port = config.get('Finance', 'finance_bdihostport')
    user = config.get('Finance', 'finance_bdihostuser')
    passwd = config.get('Finance', r'finance_bdihostpasswd')

    #获取本地存放路径
    localfiledirtmp = config.get('Finance', 'finance_localfiledirtmp')
    if not os.path.exists(localfiledirtmp):
        print(u'目录%s不存在，新建目录！' % localfiledirtmp)
        os.makedirs(localfiledirtmp)
    #获取远端存放路径
    bdifiledir = config.get('Finance', 'finance_bdifiledir')

    #获取近6个月的账务周期
    #cycle = (datetime.datetime.now()-relativedelta(months=1)).strftime("%Y-%m")
    cycle_list = []
    for n in range(6):
        cycle_list.append((datetime.datetime.now() - relativedelta(months=n)).strftime("%Y-%m"))

    #获取账务文件类型列表
    type_EN_list = config.get('Finance', 'finance_filetype_EN').split(', ')
    type_CN_list = config.get('Finance', 'finance_filetype_CN').split(', ')

    #获取相关账期的账务主列表
    finance_list = OprFinance.objects.filter(opr_cycle__in=cycle_list)

    #本地已存在的文件列表、文件生成时间列表
    lfile_list = []
    lfilemtime_list = []
    lfilemtime_tmp_list = []

    #从数据库获取对应账期的已存在文件列表，用以后续判断避免重复下载
    for i in range(len(finance_list)):
        lfile_list.extend(finance_list[i].file.all().values_list("opr_finance_filedetail_name", flat=True))
        lfilemtime_tmp_list.extend(finance_list[i].file.all().values_list("opr_finance_filedetail_createtime", flat=True))

    lfile_list.extend(OprFinanceFiledetail.objects.filter(opr_finance__isnull=True).values_list("opr_finance_filedetail_name", flat=True))
    lfilemtime_tmp_list.extend(OprFinanceFiledetail.objects.filter(opr_finance__isnull=True).values_list("opr_finance_filedetail_createtime", flat=True))
    for lfilemtime in lfilemtime_tmp_list:
        lfilemtime_list.append(lfilemtime.strftime("%Y-%m-%d %H:%M:%S"))

    #文件是否更新标识
    isupdate = 'false'

    #根据主机列表进行文件下载
    for host in hostip_list:
        print(u'-------------主机：%s-------------' %host)
        client, sftp = sftpconnect("Finance_BDI", host=host, port=port, user=user, passwd=passwd)
        file_list, filemtime_list = getFilesListInRemoteHost(sftp, bdifiledir)

        #需要下载的文件列表、文件时间列表、是否新文件标识列表、文件类型列表
        dfile_list = []
        dfilemtime_list = []
        disnew_list = []
        dtype_list = []

        #检查文件是否为新增或新修改
        for x in range(len(file_list)):
            #避免重复标识符
            flag = "false"

            #截取文件名
            filename = file_list[x].split('/')[-1]
            for i in range(len(type_EN_list)):
                #判断是否为指定类型范围内的账务文件
                if filename.lower().find(type_EN_list[i]) != -1:
                    for j,item in enumerate(lfile_list):
                        if item == filename:
                            if filemtime_list[x] > lfilemtime_list[j]:
                                #print(u'文件%s本地为旧文件，将进行下载！' %filename)
                                dfile_list.append(file_list[x])
                                dfilemtime_list.append(filemtime_list[x])
                                disnew_list.append('no')
                                dtype_list.append(type_CN_list[i])
                            else:
                                print(u'文件%s本地已为最新文件，不进行下载！' %filename)

                            #标识已被处理，避免重复处理
                            flag = "true"

                    if flag == "false":
                        print(u'文件%s本地无此文件，将进行下载！' % filename)
                        dfile_list.append(file_list[x])
                        dfilemtime_list.append(filemtime_list[x])
                        disnew_list.append('yes')
                        dtype_list.append(type_CN_list[i])

        # 若下载清单不为空，则进行整个目录文件下载
        if dfile_list:
            #判断本地临时目录是否存在
            if not os.path.exists(localfiledirtmp):
                os.makedirs(localfiledirtmp)

            result = sftpGetRemoteHostDir(sftp, localfiledirtmp, bdifiledir, type='Finance_BDI',
                                 dfile_list=dfile_list, dfilemtime_list=dfilemtime_list,
                                 disnew_list=disnew_list, dtype_list=dtype_list)
            #判断是否存在新下载文件
            if not result:
                #文件是否更新标识为已更新
                isupdate = 'true'
        sftpDisconnect(client)
        print(u'--------------------------------------------')

    print('所有主机的账务文件下载结束！')

    return isupdate

#CMIOT账务文件管理页面——文件整理方法
def cFinanceMgntClassify():
    print('开始整理账务文件..................')
    #获取本地存放路径
    localfiledirtmp = config.get('Finance', 'finance_localfiledirtmp')
    localfiledir = os.path.join(config.get('Finance', 'finance_localfiledir'), '原始文件')

    #进行账务文件整理
    filelist = filesClassify(localfiledirtmp, localfiledir)

    print('账务文件整理结束！')
    return filelist

#CMIOT账务文件管理页面——文件校验方法
def cFinanceFileCheck():
    return

#CMIOT账务文件管理页面——文件上传账务文件稽核服务器方法
def cFinanceFileSftp(filelist):
    print('开始上传账务文件到稽核服务器方法...........')

    #获取MDS主机IP列表、端口、账号信息
    host = config.get('Finance', 'finance_financehostip')
    port = config.get('Finance', 'finance_financehostport')
    user = config.get('Finance', 'finance_financehostuser')
    passwd = config.get('Finance', r'finance_financehostpasswd')

    #获取远端存放路径
    financefiledir = config.get('Finance', 'finance_financefiledir')

    print(u'-------------主机：%s-------------' % host)
    client, sftp = sftpconnect("Finance_BDI", host=host, port=port, user=user, passwd=passwd)
    sshd = ssh_connect("Finance_Reco")
    file_fail_list = sftpPutRemoteHostDir(sftp=sftp, sshd=sshd, localdir='', remotedir=financefiledir,
                                  type='Finance_BDI', filelist=filelist)

    print('所有账务文件上传结束！')

    return file_fail_list







#测试用
def cFinanceTest():

    localfiledir = config.get('Finance', 'finance_localfiledir')
    print(localfiledir)

    print(os.path.join(localfiledir, '原始文件'))

    return