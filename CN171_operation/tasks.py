#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/12/19 10:43
# @Author: zhulong
# @File  : tasks.py
# @Software: CN171

#调用celery中的task模块
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.db.models import Q

from CN171_operation.action import *
from CN171_operation.models import OprFinanceUploadRecord

@shared_task
def cFinanceFileDownloadTask():
    print ("-----------启动账务文件下载task-----------")
    isupdate = cFinanceFileDownload()

    #判断是否存在文件更新，若有更新则进行文件整理
    if isupdate == 'true':
        cFinanceMgntClassifyTask.delay()
    else:
        print("未下载新账务文件，不进行文件整理！")
    print ("-----------结束账务文件下载task-----------")


@shared_task
def cFinanceFileUploadTask():
    print ("-----------启动账务文件上传稽核服务器task-----------")

    upload_list = OprFinanceUploadRecord.objects.filter(Q(opr_finance_upload_status='待上传')
                                                        &Q(opr_finance_upload_num__lte=3))
    if upload_list:
        for upload in upload_list:

            #若失败列表不为空，则表明上传列表中部分文件已上传完成
            if not upload.opr_finance_upload_faillist:
                filelist = upload.opr_finance_upload_list
            else:
                filelist = upload.opr_finance_upload_faillist

            #从数据库text类型字段中获取文件列表
            filelist = filelist.replace("'", "").strip("[]").strip().split(', ')

            #进行文件上传，返回上传失败文件列表
            file_fail_list = cFinanceFileSftp(filelist)
            if not file_fail_list:
                upload.opr_finance_upload_status = '已上传'
                upload.opr_finance_upload_num += 1
            else:
                upload.opr_finance_upload_faillist = file_fail_list
                upload.opr_finance_upload_num += 1
                if upload.opr_finance_upload_num >= 3:
                    #重试3次均上传失败，则记录异常后不再处理
                    upload.opr_finance_upload_status = '上传异常'
            upload.save()

    else:
        print("账务文件上传记录表未发现需要上传的文件清单，不进行账务文件上传！")

    print ("-----------结束账务文件上传稽核服务器task-----------")


@shared_task
def cFinanceMgntClassifyTask():
    filelist = cFinanceMgntClassify()

    if filelist:
        record = OprFinanceUploadRecord()
        record.opr_finance_upload_status = '待上传'
        record.opr_finance_upload_list = filelist
        record.save()
        print('本次下载的账务文件已记录到上传记录表中，待上传稽核服务器！')