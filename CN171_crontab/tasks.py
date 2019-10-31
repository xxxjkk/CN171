#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/10/10 19:56
# @Author: zhulong
# @File  : tasks.py
# @Software: CN171

#调用celery中的task模块
from __future__ import absolute_import, unicode_literals
from celery import shared_task
import time
from CN171_tools import mailutils


@shared_task
def getMail():
    print ("-----------启动邮件下载task-----------")
    mailutils.retrMail()
    print ("-----------结束邮件下载task-----------")


@shared_task
def bgaction():
    return "成功"