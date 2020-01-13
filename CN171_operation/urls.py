#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/12/4 14:51
# @Author: zhulong
# @File  : urls.py
# @Software: CN171

from django.conf.urls import url
from CN171_operation import views as oprviews


urlpatterns = [
    #CMIOT账务文件管理页面
    url(r'^cmiotFinanceManagement/', oprviews.cFinanceMgnt, name='cFinanceMgnt'),
    #CMIOT账务文件管理页面--查询
    url(r'^cmiotFinanceMgntSearch/', oprviews.cFinanceMgntSearch, name='cFinanceMgntSearch'),
    #CMIOT账务文件管理页面--上传跳转
    url(r'^cmiotFinanceMgntUploadGoto/', oprviews.cFinanceMgntUploadGoto, name='cFinanceMgntUploadGoto'),
    #CMIOT账务文件管理页面--上传处理
    url(r'^cmiotFinanceMgntUpload/', oprviews.cFinanceMgntUpload, name='cFinanceMgntUpload'),
    #CMIOT账务文件管理页面--文件详情
    url(r'^cmiotFinanceFileDetail/', oprviews.cFinanceFileDetail, name='cFinanceFileDetail'),
    #CMIOT账务文件管理页面--校验结果
    url(r'^cmiotFinanceFileCheck/', oprviews.cFinanceFileCheckDetail, name='cFinanceFileCheckDetail'),
    # CMIOT账务文件管理页面--下载跳转
    url(r'^cFinanceMgntDownloadGoto/', oprviews.cFinanceMgntDownloadGoto, name='cFinanceMgntDownloadGoto'),


    #CMIOT账务文件稽核页面
    url(r'^cmiotFinanceReco/', oprviews.cFinanceReco, name='cFinanceReco'),
]