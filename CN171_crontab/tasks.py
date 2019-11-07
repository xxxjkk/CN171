#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/10/10 19:56
# @Author: zhulong
# @File  : tasks.py
# @Software: CN171

#调用celery中的task模块
from __future__ import absolute_import, unicode_literals
from celery import shared_task

@shared_task
def testtask():
    print ("-----------启动测试task-----------")

    print ("-----------结束测试task-----------")