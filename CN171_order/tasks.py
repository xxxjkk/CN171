#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/10/25 10:01
# @Author: zhulong
# @File  : tasks.py.py
# @Software: CN171

#调用celery中的task模块
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from CN171_tools import mailutils
from CN171_order import excelutils


@shared_task
def getMail():
    print ("-----------启动邮件下载task-----------")
    mailutils.retrMail()
    print ("-----------结束邮件下载task-----------")

@shared_task
def excelRead():
    print ("-----------启动excel读取task-----------")
    excelutils.excelread()
    print ("-----------结束excel读取task-----------")