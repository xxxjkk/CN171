#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/12/19 10:43
# @Author: zhulong
# @File  : tasks.py
# @Software: CN171

#调用celery中的task模块
from __future__ import absolute_import, unicode_literals

import zipfile

from celery import shared_task
from django.db.models import Q
from django.core.cache import cache

from CN171_operation.action import *
from CN171_operation.models import OprFinanceUploadRecord

#账务文件从BDI服务器下载定时任务
@shared_task
def cFinanceFileDownloadTask():
    print ("-----------启动账务文件下载task-----------")
    #每次下载前，判断是否已有定时任务在下载
    downloadflag = cache.get('downloadflag')
    if downloadflag != 1:
        cache.set('downloadflag', 1)
        isupdate = cFinanceFileDownload()
        cache.set('downloadflag', 0)

        #判断是否存在文件更新，若有更新则进行文件整理
        if isupdate == 'true':
            cFinanceMgntClassifyTask.delay()
        else:
            print("未下载新账务文件，不进行文件整理！")
    print ("-----------结束账务文件下载task-----------")

#账务文件上传到稽核服务器定时任务
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

#账务文件整理定时任务
@shared_task
def cFinanceMgntClassifyTask():
    #每次下载前，判断是否已有定时任务在下载
    classifyflag = cache.get('classifyflag')
    if classifyflag != 1:
        cache.set('classifyflag', 1)
        filelist = cFinanceMgntClassify()
        if filelist:
            record = OprFinanceUploadRecord()
            record.opr_finance_upload_status = '待上传'
            record.opr_finance_upload_list = filelist
            record.save()
            print('本次下载的账务文件已记录到上传记录表中，待上传稽核服务器！')
        cache.set('classifyflag', 0)

#账务文件下载压缩包任务
@shared_task
def financeFileZip(page, **kwargs):
    #获取文件下载目录
    downloaddir = config.get('Finance', 'finance_downloaddir')
    # 需要下载文件列表
    filename_list = []
    filedir_list = []
    filename = ''

    if page == 'financedownloadmgnt':
        area_list = kwargs['area_list']
        type_list = kwargs['type_list']
        cycle_list = kwargs['cycle_list']

        #获取相关账期的账务主列表
        finance_list = OprFinance.objects.filter(opr_area__in=area_list, opr_cycle__in=cycle_list)

        #获取需要打包的文件列表
        for i in range(len(finance_list)):
            filedir_list.extend(finance_list[i].file.filter(opr_finance_filedetail_type__in=type_list).values_list
                                ("opr_finance_filedetail_dir", flat=True))
            filename_list.extend(finance_list[i].file.filter(opr_finance_filedetail_type__in=type_list).values_list
                                 ("opr_finance_filedetail_name", flat=True))

        filename = 'financefiles_' + time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.zip'

    elif page == 'financefiledetail':
        id_list = kwargs['id_list']
        # 获取需要打包的文件列表
        filedir_list.extend(OprFinanceFiledetail.objects.filter(opr_finance_filedetail_id__in=id_list).values_list
                            ("opr_finance_filedetail_dir", flat=True))
        filename_list.extend(OprFinanceFiledetail.objects.filter(opr_finance_filedetail_id__in=id_list).values_list
                             ("opr_finance_filedetail_name", flat=True))

        filename = 'financefiles_' + time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.zip'

    elif page == 'recodownload':
        id_list = kwargs['id_list']
        # 获取需要打包的文件列表
        filedir_list.extend(OprFinanceReco.objects.filter(opr_finance_reco_id__in=id_list).values_list
                            ("opr_finance_reco_filedir", flat=True))
        filename_list.extend(OprFinanceReco.objects.filter(opr_finance_reco_id__in=id_list).values_list
                             ("opr_finance_reco_file", flat=True))

        filename = 'financerecofiles_' + time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.zip'

    # 将所有账务文件打包到zip文件
    filepath = os.path.join(downloaddir, filename)
    zipf = zipfile.ZipFile(file=filepath, mode='a')
    length = len(filedir_list)
    for j, filedir in enumerate(filedir_list):
        file = os.path.join(filedir, filename_list[j])
        zipf.write(file)

        #更新进度
        percent = (j+1) * 100 / length
        #保留2位小数
        cache.set('percent', round(percent, 2))

    zipf.close()

    cache.set('filename', filename)

#账务文件稽核定时任务
@shared_task
def cFinanceRecoTask():
    #获取待执行的稽核列表
    try:
        reco_list = OprFinanceReco.objects.filter(Q(opr_finance_reco_result='准备稽核'))
        for reco in reco_list:
            print(reco.opr_finance.opr_area)
            print(reco.opr_finance.opr_cycle)

    except ObjectDoesNotExist:
        print('√选的省份未找到相关数据，请检查！')
